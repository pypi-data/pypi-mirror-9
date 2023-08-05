from . import setup


def before_all(context):
    setup(context)


def before_feature(context, feature):
    pass


def before_scenario(context, scenario):
    context.personas = {}
    context.persona = None


def after_feature(context, feature):
    pass


def after_scenario(context, scenario):
    pass


def after_all(context):
    pass
