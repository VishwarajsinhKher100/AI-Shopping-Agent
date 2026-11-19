import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from shopping_agent.setup_db import (
    create_order,
    get_product_by_name,
    search_products,
)

MODEL_NAME = "openai/gpt-oss-120b"


class ShoppingIntent(BaseModel):
    action: Literal["search", "order", "other"] = Field(
        description="Search products, order one exact product, or handle an unrelated request."
    )
    query: str = Field(
        default="",
        description="Short product/category keywords for a product search.",
    )
    max_price: float | None = Field(
        default=None,
        description="Maximum product price in dollars, if requested.",
    )
    min_rating: float | None = Field(
        default=None,
        description="Minimum average review rating, if requested.",
    )
    organic: bool = Field(
        default=False,
        description="Whether the user explicitly requires an organic product.",
    )
    product_name: str | None = Field(
        default=None,
        description="Exact catalog product name to order, if the user requested an order.",
    )


@dataclass
class ShoppingResponse:
    message: str
    products: list[dict]


class ShoppingAgent:
    def __init__(self) -> None:
        load_dotenv()
        self._chain = None

    def _get_chain(self):
        if self._chain is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "GROQ_API_KEY is missing. Add your GroqCloud API key to the environment or .env file."
                )

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a shopping assistant for a catalog of grocery products. "
                        "Classify each user message into a shopping intent. For searches, "
                        "extract only useful product/category keywords and the requested "
                        "price, minimum average rating, and organic filters. For orders, "
                        "return the exact catalog product name only when the user explicitly "
                        "asks to buy/order a specific item. Never invent product names. "
                        "The catalog includes honey, oils, nuts, seeds, grains, tea, coffee, "
                        "snacks, and dairy alternatives. Use action='other' when clarification "
                        "or a non-shopping response is appropriate."
                    ),
                    ("human", "{message}"),
                ]
            )
            model = ChatGroq(
                model=MODEL_NAME,
                temperature=0,
                api_key=api_key,
            )
            self._chain = prompt | model.with_structured_output(ShoppingIntent)
        return self._chain

    def handle_message(self, message: str) -> ShoppingResponse:
        intent: ShoppingIntent = self._get_chain().invoke({"message": message})

        if intent.action == "search":
            products = search_products(
                query=intent.query,
                max_price=intent.max_price,
                min_rating=intent.min_rating,
                organic=intent.organic,
            )
            if not products:
                return ShoppingResponse(
                    message="I couldn't find products matching those filters. Try adjusting your search.",
                    products=[],
                )
            return ShoppingResponse(
                message=f"I found {len(products)} matching product(s):",
                products=products,
            )

        if intent.action == "order":
            if not intent.product_name:
                return ShoppingResponse(
                    message="Which specific product would you like to order?",
                    products=[],
                )
            product = get_product_by_name(intent.product_name)
            if product is None:
                return ShoppingResponse(
                    message=(
                        f"I couldn't find an exact catalog match for "
                        f"'{intent.product_name}'. Search for the item and choose it from the results."
                    ),
                    products=[],
                )
            order_id = create_order(product["id"])
            if order_id is None:
                return ShoppingResponse(
                    message="That product is no longer available to order. Please search again.",
                    products=[],
                )
            return ShoppingResponse(
                message=f"Order #{order_id} placed for **{product['name']}** (${product['price']:.2f}).",
                products=[],
            )

        return ShoppingResponse(
            message="I can help find products or place an order. What are you shopping for?",
            products=[],
        )
