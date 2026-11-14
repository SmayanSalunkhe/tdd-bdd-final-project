"""Selenium step definitions for the Product administration UI."""
import logging

from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

ID_PREFIX = "product_"


def _element(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    return WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )


@when('I visit the "Home Page"')
def step_visit_home(context):
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_title_contains(context, message):
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_text_absent(context, text_string):
    assert text_string not in context.driver.find_element(By.TAG_NAME, "body").text


@when('I set the "{element_name}" to "{text_string}"')
def step_set_field(context, element_name, text_string):
    element = _element(context, element_name)
    element.clear()
    element.send_keys(text_string)


@when('I change "{element_name}" to "{text_string}"')
def step_change_field(context, element_name, text_string):
    element = _element(context, element_name)
    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_select_dropdown(context, text, element_name):
    Select(_element(context, element_name)).select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_dropdown_value(context, text, element_name):
    selected = Select(_element(context, element_name)).first_selected_option.text
    assert selected.lower() == text.lower()


@then('the "{element_name}" field should be empty')
def step_field_empty(context, element_name):
    assert _element(context, element_name).get_attribute("value") == ""


@when('I copy the "{element_name}" field')
def step_copy_field(context, element_name):
    context.clipboard = _element(context, element_name).get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_paste_field(context, element_name):
    element = _element(context, element_name)
    element.clear()
    element.send_keys(context.clipboard)


@when('I press the "{button_name}" button')
def step_press_button(context, button_name):
    button_id = button_name.lower().replace(" ", "-") + "-btn"
    WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.element_to_be_clickable((By.ID, button_id))
    ).click()


@then('I should see the message "{message}"')
def step_message_present(context, message):
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, "flash_message"))
    )
    assert message.lower() in element.text.lower()


@then('I should not see the message "{message}"')
def step_message_absent(context, message):
    element = context.driver.find_element(By.ID, "flash_message")
    assert message.lower() not in element.text.lower()


@then('I should see "{text_string}" in the "{element_name}" field')
def step_field_contains(context, text_string, element_name):
    element = _element(context, element_name)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element.get_attribute("id")), text_string
        )
    )
    assert found


@then('I should see "{product_name}" in the results')
def step_result_present(context, product_name):
    results = context.driver.find_element(By.ID, "search_results")
    assert product_name in results.text


@then('I should not see "{product_name}" in the results')
def step_result_absent(context, product_name):
    results = context.driver.find_element(By.ID, "search_results")
    assert product_name not in results.text
