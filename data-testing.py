from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import(
    SystemMessage,
    HumanMessage,
    AIMessage
)
import streamlit as st
from streamlit_chat import message
from langchain import PromptTemplate
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)


st.set_page_config(
    page_title='Data Testing',
    page_icon='🤖'
)

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'button_disabler' not in st.session_state:
    st.session_state.button_disabler = True

if 'prompt' not in st.session_state:
    st.session_state.prompt = ''

## Sql code and primary keys input start Enabled
if 'sql_code_input_disabler' not in st.session_state:
    st.session_state.sql_code_input_disabler = False

if 'primary_keys_input_disabler' not in st.session_state:
    st.session_state.primary_keys_input_disabler = False

# button starts visible
if 'button_visibility' not in st.session_state:
    st.session_state.button_visibility = True

# chat starts invisible
if 'chat_input_visibility' not in st.session_state:
    st.session_state.chat_input_visibility = False

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# Orchestrates the initialization of session_states
def clear_session_states():
    st.session_state.messages = []
    st.session_state.button_disabler = True
    st.session_state.sql_code = ''
    st.session_state.primary_keys = ''
    st.session_state.prompt = ''
    st.session_state.sql_code_input_disabler = False
    st.session_state.primary_keys_input_disabler = False
    st.session_state.button_visibility = True
    del st.session_state.generate_doc


def disable_inputs():
    st.session_state.sql_code_input_disabler = True
    st.session_state.primary_keys_input_disabler = True
    st.session_state.button_visibility = False

with st.sidebar:
    '''
        Something will be added here eventually
    '''
    st.divider()

# setting the behaviour of the system message (role)
system_message = '''You are a professional Developer specialized in writing tests for SQL Code in Goog Big Query Syntax. Your jobe is to follow the user's instructions meticulously.'''

# instantiating the ChatGPT model
chat = ChatOpenAI(model_name='gpt-4-0125-preview', temperature=0, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])

# if check_password():
st.subheader('SQL Code Documentation Assistant 🤖')


st.markdown('##### Enter the Information below to Generate a Documentation for your SQL Code')

# only visible when there's not human answer in st.session_state.messages
if st.session_state.sql_code_input_disabler == False and st.session_state.sql_code_input_disabler == False:
    st.text_input('Enter the Model Weld Reference', key = 'sql_code')
    st.text_input('Enter the tests to be created (column_name :  descripition of the test)', key = 'primary_keys')

# Enable button if sql_code and primary_keys are not empty
if st.session_state.sql_code and st.session_state.primary_keys:
    st.session_state.button_disabler = False

if st.session_state.button_visibility == True:
    st.button('Generate SQL Doc', key='generate_doc', disabled=st.session_state.button_disabler, on_click=disable_inputs)


# check if there's a instance of SystemMessage class in the session state
if not any(isinstance(msg, SystemMessage) for msg in st.session_state.messages):
    # if not, add the system message to the session state
    st.session_state.messages.append(
            SystemMessage(content=system_message)
            )

prompt_template = PromptTemplate.from_template(

    '''
    Based on the Example Below, write Tests for the new model provided by the user. The tests should be written following the same strucutre as the example below. 

    ### NEW MODEL ###
    {sql_code}

    ### TESTS TO BE DONE BASED ON THE EXAMPLE ###
    {primary_keys}

    ### EXAMPLE ###
        -- selects all data from model to be tested
        WITH data AS (
            SELECT
                *
            FROM core.website_profitability.transactions
        ),

        -- ASSERTION CTEs

        -- asserts if refunds_sales_status contains null values
        assert_RefundSalesStatus_notNull AS (
            SELECT
                'assert' as join_index,
                CASE
                    WHEN COUNT(*) > 1 THEN NULL
                ELSE 1
            END AS assert_RefundSalesStatus_notNull

            FROM data
            WHERE
                refund_sales_status is null
        ),

        -- asserts if Weight_g contains null values
        assert_WeightG_notNull AS (
            SELECT
                'assert' as join_index,
                CASE
                    WHEN COUNT(*) > 1 THEN NULL
                ELSE 1
            END AS assert_WeightG_notNull
            FROM data
            WHERE
                Weight_g is null
        ),

        -- asserts if Weight_g contains null values
        assert_PurchasingPrice_notNull AS (
            SELECT
                'assert' as join_index,
                CASE
                    WHEN COUNT(*) > 1 THEN NULL
                ELSE 1
            END AS assert_PurchasingPrice_notNull
            FROM data
            WHERE
                purchasing_price_per_unit_dkk is not null
        ),

        -- asserts if the combination of refund_sales_status and shipping_address_country is unique
        assert_RefundSalesStatus_ShippingAddressCountry_Unique AS (
            SELECT
                'assert' as join_index,
                CASE
                    WHEN COUNT(*) > 1 THEN NULL
                    ELSE 1
                END AS assert_RefundSalesStatus_ShippingAddressCountry_Unique
            FROM (
                SELECT
                    refund_sales_status,
                    shipping_address_country,
                    COUNT(*) as cnt
                FROM data
                GROUP BY refund_sales_status, shipping_address_country
                HAVING COUNT(*) > 1
            )
        ),

        -- JOIN ALL ASSERTS
        all_asserts AS (
            SELECT
                *
            FROM assert_RefundSalesStatus_notNull
            LEFT JOIN assert_WeightG_notNull USING (join_index)
            LEFT JOIN assert_PurchasingPrice_notNull USING (join_index)
            LEFT JOIN assert_RefundSalesStatus_ShippingAddressCountry_Unique USING (join_index)


        )

        -- FINAL SELECT STATEMENT
        SELECT
            *
        FROM all_asserts

    #### END OF EXAMPLE ####
    Assertions:

        Assertion 1 (assert_RefundSalesStatus_notNull): Generate a single value based on a condition applied to the refund_sales_status field. If more than one record has refund_sales_status as 'sales', output NULL; otherwise, output 1.
        Assertion 2 (assert_WeightG_notNull): Produce a single value based on a condition applied to the Weight_g field. If more than one record has Weight_g as null, output NULL; otherwise, output 1.

        '''
)  

# creating the messages (chat history) in the Streamlit session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
            SystemMessage(content=system_message)
            )

# if Button is clicked and chat input is not visible
if st.session_state.generate_doc and st.session_state.chat_input_visibility == False:
    # if this is the first message, add the prompt template
    if len(st.session_state.messages) == 1:
        st.session_state.prompt = prompt_template.format(
                sql_code=st.session_state.sql_code,
                primary_keys=st.session_state.primary_keys)
    else:
        st.session_state.prompt = st.session_state.sql_code

    st.session_state.messages.append(
        HumanMessage(content=st.session_state.prompt)
    )
    # disable sql_code and primary_keys input
    st.session_state.sql_code_input_disabler = True
    st.session_state.primary_keys_input_disabler = True

    with st.spinner('Working on your request ...'):
    # creating the ChatGPT response
        response = chat(st.session_state.messages)
    # adding the response's content to the session state
    st.session_state.messages.append(AIMessage(content=response.content))
    st.session_state.chat_input_visibility = True


# displaying the messages (chat history)
for i, msg in enumerate(st.session_state.messages[1:]):
    # if it's odd, it's a user message
    if i % 2 == 0:
        with st.chat_message("user"):
            st.markdown(st.session_state.prompt)
    # if it's even, it's a AI message
    else:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

#     st.session_state.messages.append(AIMessage(content=response.content))
