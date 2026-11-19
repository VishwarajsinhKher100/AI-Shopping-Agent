import streamlit as st

from agent import ShoppingAgent
from setup_db import create_database, create_order


SAMPLE_QUESTIONS = [
    "Find organic honey under $20 with a 4.5+ rating",
    "Show me the highest-rated organic snacks",
    "Find tea under $13",
]


@st.cache_resource
def get_agent() -> ShoppingAgent:
    return ShoppingAgent()


@st.cache_resource
def initialize_database() -> bool:
    create_database()
    return True


def main() -> None:
    st.set_page_config(page_title="AI Shopping Assistant")
    initialize_database()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("AI Shopping Assistant")
    st.caption("Find products by your preferences, then order the item you choose.")

    with st.sidebar:
        if st.button("New chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.subheader("Try asking")
        for index, question in enumerate(SAMPLE_QUESTIONS):
            if st.button(question, key=f"sample-{index}", use_container_width=True):
                st.session_state.pending_prompt = question

    for message_index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                for product in message.get("products", []):
                    with st.container(border=True):
                        st.markdown(f"**{product['name']}** | ${product['price']:.2f}")
                        st.caption(
                            f"Rating: {product['average_rating']:.2f} "
                            f"({product['review_count']} reviews) · "
                            f"{'Organic' if product['is_organic'] else 'Non-organic'}"
                        )
                        st.write(product["description"])
                        if st.button(
                            f"Order {product['name']}",
                            key=f"order-{message_index}-{product['id']}",
                        ):
                            order_id = create_order(product["id"])
                            if order_id is None:
                                order_message = "That product is no longer available to order. Please search again."
                            else:
                                order_message = (
                                    f"Order #{order_id} placed for **{product['name']}** "
                                    f"(${product['price']:.2f})."
                                )
                            st.session_state.messages.append(
                                {"role": "assistant", "content": order_message, "products": []}
                            )
                            st.rerun()

    prompt = st.chat_input("What would you like to find?")
    if prompt:
        st.session_state.pending_prompt = prompt

    pending_prompt = st.session_state.pop("pending_prompt", None)
    if pending_prompt:
        st.session_state.messages.append(
            {"role": "user", "content": pending_prompt, "products": []}
        )
        try:
            response = get_agent().handle_message(pending_prompt)
        except RuntimeError as error:
            response_message = str(error)
            response_products = []
        else:
            response_message = response.message
            response_products = response.products
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response_message,
                "products": response_products,
            }
        )
        st.rerun()


if __name__ == "__main__":
    main()
