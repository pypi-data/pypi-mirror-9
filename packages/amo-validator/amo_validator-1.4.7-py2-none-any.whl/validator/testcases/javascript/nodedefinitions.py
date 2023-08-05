import actions

#(branches,
# explicitly_dynamic,
# estab_context,
# action,
# returns, # as in yielding a value, not breaking execution
# block_statement,
#)

def node(branches=None, dynamic=False, action=None, returns=False,
         is_block=False):
    if branches is None:
        branches = ()
    return branches, dynamic, action, returns, is_block


DEFINITIONS = {
    "EmptyStatement": node(),
    "DebuggerStatement": node(),

    "Program": node(branches=("body", ), is_block=True),
    "BlockStatement": node(branches=("body", ), is_block=True),
    "ExpressionStatement": node(branches=("expression", ),
                                action=actions._expression,
                                returns=True),
    "IfStatement": node(branches=("test", "alternate", "consequent"),
                        is_block=True),
    "LabeledStatement": node(branches=("body", )),
    "BreakStatement": node(),
    "ContinueStatement": node(),
    "WithStatement": node(branches=("body", "object"),
                          action=actions._define_with, is_block=True),
    "SwitchStatement": node(branches=("test", "cases"), is_block=True),
    "ReturnStatement": node(branches=("argument", )),
    "ThrowStatement": node(branches=("argument", )),
    "TryStatement": node(branches=("block", "handler", "finalizer",
                                   "guardedHandlers"),
                         is_block=True),
    "WhileStatement": node(branches=("test", "body"), is_block=True),
    "DoWhileStatement": node(branches=("test", "body"), is_block=True),
    "ForStatement": node(branches=("init", "test", "update", "body"),
                         is_block=True),
    "ForInStatement": node(branches=("left", "right", "body"), is_block=True),

    "FunctionDeclaration": node(branches=("body", ), dynamic=True,
                                action=actions._define_function,
                                is_block=True),
    "VariableDeclaration": node(branches=("declarations", ),
                                action=actions._define_var),

    "ThisExpression": node(action=actions._get_this, returns=True),
    "ArrayExpression": node(branches=("elements", ),
                            action=actions._define_array, returns=True),
    "ObjectExpression": node(branches=("properties", ),
                             action=actions._define_obj, returns=True),
    "FunctionExpression": node(branches=("body", ), dynamic=True,
                               action=actions._func_expr, returns=True,
                               is_block=True),
    "SequenceExpression": node(branches=("expressions", ), returns=True),
    "UnaryExpression": node(branches=("argument", ),
                            action=actions._expr_unary, returns=True),
    "BinaryExpression": node(branches=("left", "right"),
                             action=actions._expr_binary, returns=True),
    "AssignmentExpression": node(branches=("left", "right"),
                                 action=actions._expr_assignment,
                                 returns=True),
    "UpdateExpression": node(branches=("argument", ), returns=True),
    "LogicalExpression": node(branches=("left", "right"), returns=True),
    "ConditionalExpression": node(branches=("test", "alternate", "consequent"),
                                  returns=True),
    "NewExpression": node(branches=("constructor", "arguments"),
                          action=actions._new, returns=True),
    "CallExpression": node(branches=("callee", "arguments"),
                           action=actions._call_expression, returns=True),
    "MemberExpression": node(branches=("object", "property"),
                             action=actions.trace_member, returns=True),
    "YieldExpression": node(branches=("argument",), returns=True),
    "ComprehensionExpression": node(branches=("body", "filter"), returns=True),
    "GeneratorExpression": node(branches=("body", "filter"), returns=True),

    "ObjectPattern": node(),
    "ArrayPattern": node(),

    "SwitchCase": node(branches=("test", "consequent")),
    "CatchClause": node(branches=("param", "guard", "body"), returns=True),
    "ComprehensionBlock": node(branches=("left", "right"), returns=True),

    "Literal": node(action=actions._define_literal, returns=True),
    "Identifier": node(action=actions._ident, returns=True),
    "GraphExpression": node(),
    "GraphIndexExpression": node(),
    "UnaryOperator": node(returns=True),
    "BinaryOperator": node(returns=True),
    "LogicalOperator": node(returns=True),
    "AssignmentOperator": node(returns=True),
    "UpdateOperator": node(returns=True),
}
