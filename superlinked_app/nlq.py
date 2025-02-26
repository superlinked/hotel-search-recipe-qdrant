import json
import urllib.request

from superlinked import framework as sl

from superlinked_app.config import settings

openai_config = sl.OpenAIClientConfig(
    api_key=settings.openai_api_key.get_secret_value(),
    model=settings.openai_model,
)


def get_cat_options() -> dict[list[str]]:
    with urllib.request.urlopen(settings.path_categories) as url:
        return json.load(url)


description_description = (
    "'description' should be one or two normalized sentences that describe the desired hotel.\n"
    "Don't include price, rating, and rating count mentions in the 'description'.\n"
    "Some examples of what should be captured in 'description': "
    "reinnovated bathroom, comfortable beds, close to museums, "
    "good connectivity, airport shuttle, elegant design, traditional cuisine.\n"
    "In case of all and every requirement is captured by other sl.Parameters (accomodation type, amenities, etc.), "
    "description should be empty.\n"
    "Examples of 'description' generation: \n"
    "1. user_query: 'hotels in historical center of London, close to museums, cheapest options' "
    "-> description: 'Hotel is located in historical center of London, close to museums.' \n"
    "2. user_query: 'not expensive apartment in calm area of Paris for a family trip, airport shuttle, many reviews' "
    "-> description: 'Apartment is located in calm area in Paris, suitable for a family trip. Airport shuttle is available.' \n"
    "3. user_query: 'hostels in Berlin centre for huge company' "
    "-> description: 'Hostel is located in the center of Berlin, suitable for a huge company.' \n"
    "4. user_query: 'Affordable dog-friendly hotels with few reviews' "
    "-> description: '' \n"
)

city_description = (
    "Name of the city like 'London' or 'Paris'.\n"
    "If famous toponim is mentioned, use relevant city, for example: "
    "'London' for Trafalgar Sq or 'Paris' for Eiffel Tower.\n"
    "If city can't be determined, use None for 'city'.\n"
)

price_description = (
    "Weight of the price. "
    "Higher value means more expensive hotels, "
    "lower value means cheaper ones. "
    "Weight depends on the adjective or noun used to describe the price. "
    "For example: "
    "positive weight: 'expensive', 'not cheap', 'high price', 'luxurious', 'very expensive', 'the most expensive', 'highest price'; "
    "negative weight: 'cheap', 'not expensive', 'affordable', 'low price', 'the cheapest', 'lowest price'; "
    "0 should be used if no preference for the price."
)

rating_description = (
    "Weight of the rating. "
    "Higher value means higher rating, "
    "lower value means lower rating. "
    "Weight depends on the adjective or noun used to describe the rating. "
    "For example: "
    "positive weight: 'high rating', 'good', 'higly-rated', 'highest rating', 'best', 'top-rated'; "
    "negative weight: 'low rating', 'poor', 'not recommended', 'lowest rating', 'worst', 'not recommended'; "
    "0 should be used if no preference for the rating."
)

rating_count_description = (
    "Weight of the rating count. "
    "Higher value means more reviews, "
    "lower value means fewer reviews. "
    "Weight depends on the adjective or noun used to describe the rating count. "
    "For example: "
    "positive weight: 'many reviews', 'popular', 'highly reviewed', 'most reviewed', 'most popular', 'highest reviews'; "
    "negative weight: 'few reviews', 'not popular', 'seldom reviewed', 'least reviewed', 'least popular', 'lowest reviews'; "
    "0 should be used if no preference for the rating count."
)

accomodation_type_description = (
    "If users searches for some hotels, include 'Hotel' in accomodation types, "
    "same for other accomodation types."
)

system_prompt = (
    "Extract the search parameters from the user query.\n"
    "Advices:\n"
    "**'include' and 'exclude' attributes**\n"
    "Use relevant amenities, for example, include 'Cot' when user mentions 'baby',"
    "and exclude it when user mentions 'no children'.\n"
    "If no amenities are mentioned, use None for 'include' and 'exclude'.\n"
    "**'accomodation_type'**\n"
    "If users searches for some hotels, include 'Hotel' in accomodation types, "
    "same for other accomodation types.\n"
)
