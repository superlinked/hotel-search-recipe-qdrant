from superlinked import framework as sl

from superlinked_app.config import settings


@sl.schema
class Hotel:
    # `id` is obligatory field
    id: sl.IdField
    #
    # the fields below are embedded into spaces
    # and used for for semantic search
    description: sl.String
    price: sl.Float
    rating: sl.Float
    rating_count: sl.Integer
    #
    # this attributes are not embedded
    # and used only for hard-filtering
    accomodation_type: sl.String
    property_amenities: sl.StringList
    room_amenities: sl.StringList
    wellness_spa: sl.StringList
    accessibility: sl.StringList
    for_children: sl.StringList
    city: sl.String
    country: sl.String


hotel_schema = Hotel()

# desciption is embedded using sentence-transformer model
# model_name is defined in `config.py`
description_space = sl.TextSimilaritySpace(
    text=hotel_schema.description,
    model=settings.text_embedder_name,
)

# rating is embedded using linear scale
rating_space = sl.NumberSpace(
    hotel_schema.rating,
    min_value=0,
    max_value=10,
    mode=sl.Mode.MAXIMUM,
)

# price and rating_count are embedded using logarithmic scale
# because their distribution spans multiple orders of magnitude
price_space = sl.NumberSpace(
    hotel_schema.price,
    min_value=0,
    max_value=1000,
    mode=sl.Mode.MAXIMUM,
    scale=sl.LogarithmicScale(),
)


rating_count_space = sl.NumberSpace(
    hotel_schema.rating_count,
    min_value=0,
    # max_value is calculated from the dataset as 99.5% quantile
    # check `notebooks/eda.ipynb` for details
    max_value=22500,
    mode=sl.Mode.MAXIMUM,
    scale=sl.LogarithmicScale(),
)

# index is a composition of spaces
index = sl.Index(
    spaces=[
        description_space,
        price_space,
        rating_space,
        rating_count_space,
    ],
    #
    # the fields below are used for hard-filtering
    fields=[
        hotel_schema.price,
        hotel_schema.rating,
        hotel_schema.city,
        hotel_schema.country,
        hotel_schema.accomodation_type,
        hotel_schema.property_amenities,
        hotel_schema.room_amenities,
        hotel_schema.wellness_spa,
        hotel_schema.accessibility,
        hotel_schema.for_children,
    ],
)
