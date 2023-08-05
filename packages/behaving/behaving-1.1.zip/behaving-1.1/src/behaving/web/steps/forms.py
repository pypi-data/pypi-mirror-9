import os
from behave import step
from splinter.exceptions import ElementDoesNotExist

from behaving.personas.persona import persona_vars


@step(u'I fill in "{name}" with "{value}"')
@persona_vars
def i_fill_in_field(context, name, value):

        context.browser.fill(name, value)


@step(u'I clear field "{name}"')
@persona_vars
def i_clear_field(context, name):

    el = context.browser.find_element_by_name(name)
    assert el, 'Element not found'
    el.clear()


@step(u'I type "{value}" to "{name}"')
@persona_vars
def i_type_to(context, name, value):

    for key in context.browser.type(name, value, slowly=True):
        assert key


@step(u'I choose "{value}" from "{name}"')
@persona_vars
def i_choose_in_radio(context, name, value):
    context.browser.choose(name, value)


@step(u'I check "{name}"')
@persona_vars
def i_check(context, name):

    context.browser.check(name)


@step(u'I uncheck "{name}"')
@persona_vars
def i_uncheck(context, name):

    context.browser.uncheck(name)


@step(u'I toggle "{name}"')
def i_toggle(context, name):

    el = context.browser.find_by_name('digest')
    assert el, u'Element not found'
    el = el.first
    if el.checked:
        el.uncheck()
    else:
        el.check()


@step(u'I select "{value}" from "{name}"')
@persona_vars
def i_select(context, value, name):
    try:
        context.browser.select(name, value)
    except ElementDoesNotExist:
        inp = context.browser.find_by_xpath("//input[@name='%s'][@value='%s']" % (name, value))
        assert inp, u'Element not found'
        inp.first.check()


@step(u'I press "{name}"')
@persona_vars
def i_press(context, name):

    element = context.browser.find_by_xpath(
        ("//*[@id='%(name)s']|"
         "//*[@name='%(name)s']|"
         "//button[contains(text(), '%(name)s')]|"
         "//a[contains(text(), '%(name)s')]") % {'name': name})
    assert element, u'Element not found'
    element.first.click()


@step(u'I press the element with xpath "{xpath}"')
@persona_vars
def i_press_xpath(context, xpath):

    button = context.browser.find_by_xpath(xpath)
    assert button, u'Element not found'
    button.first.click()


@step('I attach the file "{path}" to "{name}"')
@persona_vars
def i_attach(context, name, path):
    if not os.path.exists(path):
        path = os.path.join(context.attachment_dir, path)
        if not os.path.exists(path):
            assert False
    context.browser.attach_file(name, path)


@step('I set the inner HTML of the element with id "{id}" to "{contents}"')
@persona_vars
def set_html_content_to_element_with_id(context, id, contents):
    assert context.browser.evaluate_script("document.getElementById('%s').innerHTML = '%s'" % (id, contents)), \
        u'Element not found or could not set HTML content'


@step('I set the inner HTML of the element with class "{klass}" to "{contents}"')
@persona_vars
def set_html_content_to_element_with_class(context, klass, contents):
    assert context.browser.evaluate_script("document.getElementsByClassName('%s')[0].innerHTML = '%s'" % (klass, contents)), \
        u'Element not found or could not set HTML content'


@step(u'field "{name}" should have the value "{value}"')
@persona_vars
def field_has_value(context, name, value):
    el = context.browser.find_by_xpath(
        ("//*[@id='%(name)s']|"
         "//*[@name='%(name)s']") % {'name': name})
    assert el, u'Element not found'
    assert el.first.value == value, "Values do not match, expected %s but got %s" % (value, el.first.value)


@step(u'"{name}" should be enabled')
@persona_vars
def is_enabled(context, name):
    el = context.browser.find_by_xpath(
        ("//*[@id='%(name)s']|"
         "//*[@name='%(name)s']") % {'name': name})
    assert el, u'Element not found'
    assert el.first._element.is_enabled()


@step(u'"{name}" should be disabled')
@step(u'"{name}" should not be enabled')
@persona_vars
def is_disabled(context, name):
    el = context.browser.find_by_xpath(
        ("//*[@id='%(name)s']|"
         "//*[@name='%(name)s']") % {'name': name})
    assert el, u'Element not found'
    assert not el.first._element.is_enabled()


@step(u'field "{name}" should be valid')
@persona_vars
def field_is_valid(context, name):
    assert context.browser.find_by_name(name), u'Element not found'
    assert context.browser.evaluate_script("document.getElementsByName('%s')[0].checkValidity()" % name), \
        'Field is invalid'


@step(u'field "{name}" should be invalid')
@step(u'field "{name}" should not be valid')
@persona_vars
def field_is_invalid(context, name):
    assert context.browser.find_by_name(name), u'Element not found'
    assert not context.browser.evaluate_script("document.getElementsByName('%s')[0].checkValidity()" % name), \
        'Field is valid'


@step(u'field "{name}" should be required')
@persona_vars
def field_is_required(context, name):
    assert context.browser.find_by_name(name), u'Element not found'
    assert context.browser.evaluate_script("document.getElementsByName('%s')[0].getAttribute('required')" % name), \
        'Field is not required'


@step(u'field "{name}" should not be required')
@persona_vars
def field_is_not_required(context, name):
    assert context.browser.find_by_name(name), u'Element not found'
    assert not context.browser.evaluate_script("document.getElementsByName('%s')[0].getAttribute('required')" % name), \
        'Field is required'


@step(u'I enter "{text}" to the alert')
@persona_vars
def set_alert_text(context, text):
    alert = context.browser.driver.switch_to_alert()
    assert alert, u'Alert not found'
    alert.send_keys(text)


@step(u'I accept the alert')
@persona_vars
def accept_alert(context):
    alert = context.browser.driver.switch_to_alert()
    assert alert, u'Alert not found'
    alert.accept()


@step(u'I dismiss the alert')
@persona_vars
def dimiss_alert(context):
    alert = context.browser.driver.switch_to_alert()
    assert alert, u'Alert not found'
    alert.dismiss()
