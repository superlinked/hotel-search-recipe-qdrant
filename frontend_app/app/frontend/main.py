import uuid
import json

import streamlit as st

from app.superlinked import SuperlinkedClient

from app.utils.logging import setup_logging
from app.utils.utils import (
    load_image_urls,
    get_kick_start_options,
    flatten_response,
    clean_knn_params,
)
from app.frontend.components import format_header, format_amenities, format_filters

from app.config import settings


logger = setup_logging()

st.set_page_config(
    page_title="Superlinked hotel search demo",
    initial_sidebar_state="expanded",
    layout="centered",
    page_icon="app/frontend/favicon.png"
    
)


# Custom CSS to remove rounded corners
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');

    /* Apply DM Mono to all headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'DM Mono', monospace !important;
    }

    /* Custom styling for the text input and its containers */
    .stTextInput input {
        height: 60px !important;
        font-size: 16px !important;
        padding: 12px !important;
    }

    div[data-testid="stTextInputRootElement"] {
        min-height: 60px !important;
    }

            
    /* Styling for number input to match text input */
    .stNumberInput input {
        height: 60px !important;
        font-size: 16px !important;
        padding: 12px !important;
    }

    div[data-testid="stNumberInputContainer"] {
        min-height: 60px !important;
    }

            
    /* Custom info box styling */
    div[data-testid="stAlert"] {
        background-color: #FFDDD5 !important;
    }
    
    div[data-testid="stAlertContentInfo"] {
        color: #FE552E !important;
    }
             
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_resources():
    sl_client = SuperlinkedClient()
    id_to_image_url = load_image_urls(settings.path_dataset)
    return sl_client, id_to_image_url


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


sl_client, id_to_image_url = load_resources()

# - - - Page header - - -

st.title("Hotels search")

# Add some space between the filters and the results
st.text(" ")
st.text(" ")


kick_start_options = get_kick_start_options()


cols = st.columns(len(kick_start_options))

for option, col in zip(kick_start_options, cols):
    if col.button(option, use_container_width=True):
        st.session_state.text = option

#Space
st.text(" ")


col_query_text, col_limit = st.columns([0.8, 0.2])
with col_query_text:
    st.write("**Natural Language Search**")
    text = st.text_input(
        label="🧠 **Natural Language Interface**",
        value=kick_start_options[0],
        placeholder="What are you searching for?",
        key="text",
        label_visibility="collapsed",
    )

with col_limit:
    st.write("**Limit**")
    limit = st.number_input(
        "**Limit**", min_value=1, value=5, label_visibility="collapsed"
    )
    


# # - - - Query - - -

with st.sidebar:
    st.subheader("Description")
    st.text("Use this tool to search for hotels based on various criteria such as description, price, rating, and more, all through natural language queries.")
    st.info(
        (
            "Read more about this demo [here]"
            "(https://docs.superlinked.com/recipes/multi-modal-semantic-search/hotel-search)"
            "!"
        ),
        icon="💡",
    )

    #Add some space
    st.text(" ")
    st.text(" ")

    st.markdown("### Query params")
    st.text("This are the query parameters that superlinked created from your natural language query")

params = {"natural_query": text, "limit": limit}
response = sl_client.query("hotel", params)
response_flattened = flatten_response(response)
knn_params = response["metadata"]["search_params"]

with st.sidebar:
    knn_params_clean = clean_knn_params(knn_params)
    updated_query = st.text_area(
        label="Query params",
        value=json.dumps(knn_params_clean, indent=2),
        height=700,
        label_visibility="collapsed",
    )

# # - - - Logging - - -

log_object = {
    "session_id": st.session_state.session_id,
    "params": knn_params,
    "natural_query": text,
    "response_ids": [x["id"] for x in response_flattened],
}
logger.info(log_object)


# # - - - Rendering results - - -


filters_formatted = format_filters(knn_params)

st.markdown("---")


if filters_formatted:
    st.markdown("##### Applied filters")
    st.markdown(filters_formatted)
else:
    st.markdown("##### No filters applied")

# Add some space between the filters and the results
st.text(" ")
st.text(" ")

if len(response_flattened) > 0:

    for item in response_flattened:
        with st.container(border=True):

            col_main, col_amenities = st.columns([0.6, 0.4])

            with col_main:
                col_image, col_text = st.columns([0.4, 0.6])
                with col_image:
                    url = id_to_image_url[item["id"]]
                    try:
                        st.image(url)
                    except Exception as e:
                        st.write("🏙️ No image available")
                with col_text:
                    st.markdown(format_header(item))

                description = item["description"]
                if len(description.split()) < 3:
                    description = "No description available"
                st.markdown("*" + description + "*")

            with col_amenities:
                st.markdown(format_amenities(item, knn_params))

else:
    st.info("No results found. Please try another query.", icon="🔎")
