from collections import namedtuple

from superlinked import framework as sl

from superlinked_app.index import (
    description_space,
    hotel_schema,
    index,
    price_space,
    rating_count_space,
    rating_space,
)
from superlinked_app.nlq import (
    city_description,
    description_description,
    get_cat_options,
    openai_config,
    price_description,
    rating_count_description,
    rating_description,
    system_prompt,
)

cat_options = get_cat_options()

# query_debug is a simple way to check if server has some data ingested:
query_debug = sl.Query(index).find(hotel_schema).limit(3).select_all()

# Let's define a main query that will be used for multi-modal semantic search:
query = (
    sl.Query(
        index,
        weights={
            price_space: sl.Param(
                "price_weight",
                description=price_description,
            ),
            rating_space: sl.Param(
                "rating_weight",
                description=rating_description,
            ),
            rating_count_space: sl.Param(
                "rating_count_weight",
                description=rating_count_description,
            ),
            description_space: sl.Param("description_weight", default=1.0),
        },
    )
    .find(hotel_schema)
    .similar(
        description_space.text,
        sl.Param("description", description=description_description),
        weight=sl.Param("similar_description_weight", default=1.0),
    )
)

# We can specify number of retreved results like this:
query = query.limit(sl.Param("limit", default=4))

# We want all fields to be returned
query = query.select_all()

# .. and all the metadata including knn_params and partial_scores
query = query.include_metadata()

# Now let's add hard-filtering
# for city:
query = query.filter(
    hotel_schema.city.in_(sl.Param("city", description=city_description))
)

# ... for numerical attributes:
query = (
    query.filter(hotel_schema.price >= sl.Param("min_price"))
    .filter(hotel_schema.price <= sl.Param("max_price"))
    .filter(hotel_schema.rating >= sl.Param("min_rating"))
    .filter(hotel_schema.rating <= sl.Param("max_rating"))
)

# ... and for all categorical attributes:
CategoryFilter = namedtuple(
    "CategoryFilter", ["operator", "param_name", "category_name", "description"]
)

filters = [
    CategoryFilter(
        operator=hotel_schema.accomodation_type.in_,
        param_name="accomodation_types_include",
        category_name="accomodation_type",
        description="Accomodation types that should be included.",
    ),
    CategoryFilter(
        operator=hotel_schema.accomodation_type.not_in_,
        param_name="accomodation_types_exclude",
        category_name="accomodation_type",
        description="Accomodation types that should be excluded.",
    ),
    # Property amenities
    CategoryFilter(
        operator=hotel_schema.property_amenities.contains_all,
        param_name="property_amenities_include_all",
        category_name="property_amenities",
        description="User wants all of the following property amenities.",
    ),
    CategoryFilter(
        operator=hotel_schema.property_amenities.contains,
        param_name="property_amenities_include_any",
        category_name="property_amenities",
        description="User wants at least one of the following property amenities.",
    ),
    CategoryFilter(
        operator=hotel_schema.property_amenities.not_contains,
        param_name="property_amenities_exclude",
        category_name="property_amenities",
        description="User does not want any of the following property amenities.",
    ),
    # Room amenities
    CategoryFilter(
        operator=hotel_schema.room_amenities.contains_all,
        param_name="room_amenities_include_all",
        category_name="room_amenities",
        description="User wants all of the following room amenities.",
    ),
    CategoryFilter(
        operator=hotel_schema.room_amenities.contains,
        param_name="room_amenities_include_any",
        category_name="room_amenities",
        description="User wants at least one of the following room amenities.",
    ),
    CategoryFilter(
        operator=hotel_schema.room_amenities.not_contains,
        param_name="room_amenities_exclude",
        category_name="room_amenities",
        description="User does not want any of the following room amenities.",
    ),
    # Wellness_spa
    CategoryFilter(
        operator=hotel_schema.wellness_spa.contains_all,
        param_name="wellness_spa_include_all",
        category_name="wellness_spa",
        description="User wants all of the following wellness and spa amenities.",
    ),
    CategoryFilter(
        operator=hotel_schema.wellness_spa.contains,
        param_name="wellness_spa_include_any",
        category_name="wellness_spa",
        description="User wants at least one of the following wellness and spa amenities.",
    ),
    CategoryFilter(
        operator=hotel_schema.wellness_spa.not_contains,
        param_name="wellness_spa_exclude",
        category_name="wellness_spa",
        description="User does not want any of the following wellness and spa amenities.",
    ),
    # Accessibility
    CategoryFilter(
        operator=hotel_schema.accessibility.contains_all,
        param_name="accessibility_include_all",
        category_name="accessibility",
        description="User wants all of the following accessibility amenities.",
    ),
    CategoryFilter(
        operator=hotel_schema.accessibility.contains,
        param_name="accessibility_include_any",
        category_name="accessibility",
        description="User wants at least one of the following accessibility amenities.",
    ),
    CategoryFilter(
        operator=hotel_schema.accessibility.not_contains,
        param_name="accessibility_exclude",
        category_name="accessibility",
        description="User does not want any of the following accessibility amenities.",
    ),
    # For children
    CategoryFilter(
        operator=hotel_schema.for_children.contains_all,
        param_name="for_children_include_all",
        category_name="for_children",
        description="User wants all of the following amenities for children.",
    ),
    CategoryFilter(
        operator=hotel_schema.for_children.contains,
        param_name="for_children_include_any",
        category_name="for_children",
        description="User wants at least one of the following amenities for children.",
    ),
    CategoryFilter(
        operator=hotel_schema.for_children.not_contains,
        param_name="for_children_exclude",
        category_name="for_children",
        description="User does not want any of the following amenities for children.",
    ),
]

for filter_item in filters:
    param = sl.Param(
        filter_item.param_name,
        description=filter_item.description,
        options=cat_options[filter_item.category_name],
    )
    query = query.filter(filter_item.operator(param))

# And finally, let's add natural language interface on top
# that will call LLM to parse user natural query
# into structured superlinked query, i.e. suggest parameters values.
query = query.with_natural_query(
    natural_query=sl.Param("natural_query"),
    client_config=openai_config,
    system_prompt=system_prompt,
)
