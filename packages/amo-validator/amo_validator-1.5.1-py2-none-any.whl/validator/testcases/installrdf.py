from functools import partial

from validator import decorator
from validator.constants import PACKAGE_THEME
from validator import metadata_helpers


OPTIONS_TYPE_VALUES = ("1", "2", "3")


@decorator.register_test(tier=1)
def test_install_rdf_params(err, xpi_package=None):
    """Tests to make sure that some of the values in install.rdf
    are not gummed up."""

    if not err.get_resource("has_install_rdf"):
        return

    # We skip over install.rdf tests during bulk validation. See bug 735841.
    if err.get_resource("is_compat_test"):
        return

    install = err.get_resource("install_rdf")

    # This returns for testing reasons
    return _test_rdf(err, install)


def _test_rdf(err, install):
    """Wrapper for install.rdf testing to make unit testing so much
    easier."""

    shouldnt_exist = ("hidden", )
    if err.get_resource("listed"):
        shouldnt_exist += ("updateURL", "updateKey", )
    obsolete = ("file", "skin", "requires", )
    must_exist_once = ["id",
                       "version",
                       "name",
                       "targetApplication"]

    may_exist_once = ["about",  # For <Description> element
                      "bootstrap",
                      "optionsURL",
                      "aboutURL",
                      "iconURL",
                      "icon64URL",
                      "homepageURL",
                      "creator",
                      "multiprocessCompatible",
                      "optionsType",
                      "type",
                      "updateInfoURL",
                      "updateKey",
                      "updateURL",
                      "updateLink",  # Banned, but if not, pass it once.
                      "updateHash",
                      "signature",
                      "skinnable",
                      "strictCompatibility",
                      "unpack"]  # This has other rules; CAUTION!

    # Support a name requirement override.
    if err.overrides and err.overrides.get("ignore_empty_name"):
        must_exist_once.remove("name")
        may_exist_once.append("name")

    may_exist = ("targetApplication",
                 "localized",
                 "description",
                 "creator",
                 "translator",
                 "contributor",
                 "targetPlatform",
                 "requires",
                 "developer",)

    if (err.detected_type == PACKAGE_THEME or
        (err.subpackages and
         err.subpackages[0]["detected_type"] == PACKAGE_THEME)):
        must_exist_once.append("internalName")

    top_id = install.get_root_subject()

    for pred_raw in install.rdf.predicates(top_id, None):
        predicate = pred_raw.split("#")[-1]

        # Mark that the unpack element has been supplied
        if predicate == "unpack":
            value = install.get_object(predicate=pred_raw)
            err.save_resource("em:unpack", value, pushable=True)

        if predicate == "bootstrap":
            value = install.get_object(predicate=pred_raw)
            err.save_resource("em:bootstrap", value)

        # Test if the predicate is banned
        if predicate in shouldnt_exist:
            err.error(("testcases_installrdf",
                       "_test_rdf",
                       "shouldnt_exist"),
                      "Banned element in install.rdf",
                      """The element "%s" was found in the add-on's
                      install.rdf file. It is not allowed in add-ons under
                      the current configuration.""" % predicate,
                      "install.rdf")
            continue

        # Test if the predicate is obsolete
        if predicate in obsolete:
            err.notice(("testcases_installrdf",
                        "_test_rdf",
                        "obsolete"),
                       "Obsolete element in install.rdf",
                       "The element \"%s\" was found in the add-on's "
                       "install.rdf file. It has not been banned, but it is "
                       "no longer supported by any modern Mozilla product. "
                       "Removing the element is recommended and will not "
                       "break support." % predicate,
                       "install.rdf")
            continue

        # Remove the predicate from must_exist_once if it's there.
        if predicate in must_exist_once:

            object_value = install.get_object(top_id, pred_raw)

            # Test the predicate for specific values.
            if predicate == "id":
                _test_id(err, object_value)
            elif predicate == "version":
                _test_version(err, object_value)
            elif predicate == "name":
                _test_name(err, object_value)

            must_exist_once.remove(predicate)
            continue

        # Do the same for may_exist_once.
        if predicate in may_exist_once:

            object_value = install.get_object(top_id, pred_raw)

            if (predicate == "optionsType" and
                    str(object_value) not in OPTIONS_TYPE_VALUES):
                err.warning(
                    err_id=("testcases_installrdf", "_test_rdf",
                            "optionsType"),
                    warning="<em:optionsType> has bad value.",
                    description=[
                        "The value of <em:optionsType> must be either "
                        "%s." % ", ".join(OPTIONS_TYPE_VALUES),
                        "Value found: %s" % object_value],
                    filename="install.rdf")

            may_exist_once.remove(predicate)
            continue

        # If the element is safe for repetition, continue
        if predicate in may_exist:
            continue

        # If the predicate isn't in any of the above lists, it is
        # invalid and needs to go.
        err.notice(("testcases_installrdf",
                    "_test_rdf",
                    "unrecognized"),
                   "Unrecognized element in install.rdf",
                   ["An element was found in the install manifest, however it "
                    "does not appear to be a part of the specification, it "
                    "has been used too many times, or is not applicable to "
                    "the current configuration.",
                    "Detected element: <em:%s>" % predicate],
                   "install.rdf")

    # Once all of the predicates have been tested, make sure there are
    # no mandatory elements that haven't been found.
    if must_exist_once:
        err.error(("testcases_installrdf",
                   "_test_rdf",
                   "missing_addon"),
                  "install.rdf missing element(s).",
                  ["The element listed is a required element in the install "
                   "manifest specification. It must be added to your addon.",
                   "Missing elements: %s" % ", ".join(must_exist_once)],
                  "install.rdf")


_test_id = partial(metadata_helpers.validate_id, source="install.rdf")
_test_version = partial(
    metadata_helpers.validate_version, source="install.rdf")
_test_name = partial(metadata_helpers.validate_name, source="install.rdf")
