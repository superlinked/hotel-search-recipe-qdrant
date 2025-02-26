UNCATEGORIZED = "UNCATEGORIZED"

country_flags = {
    "Argentina": "🇦🇷",
    "Brazil": "🇧🇷",
    "Canada": "🇨🇦",
    "France": "🇫🇷",
    "Georgia": "🇬🇪",
    "Germany": "🇩🇪",
    "Hungary": "🇭🇺",
    "Indonesia": "🇮🇩",
    "Israel": "🇮🇱",
    "Italy": "🇮🇹",
    "Japan": "🇯🇵",
    "Malaysia": "🇲🇾",
    "Norway": "🇳🇴",
    "Spain": "🇪🇸",
    "Sweden": "🇸🇪",
    "Thailand": "🇹🇭",
    "Turkey": "🇹🇷",
    "USA": "🇺🇸",
    "United Kingdom": "🇬🇧",
}

columns_list = [
    "property_amenities",
    "room_amenities",
    "wellness_spa",
    "accessibility",
    "for_children",
]

amenity_emoji = {
    "accomodation_types": "🏘️",
    "property_amenities": "🏨",
    "room_amenities": "🛏️",
    "wellness_spa": "🧘",
    "accessibility": "🧑‍🦯‍➡️",
    "for_children": "👶",
}


def format_filters(params) -> str:

    lines = []

    for column in [
        "accomodation_types",
        "property_amenities",
        "room_amenities",
        "wellness_spa",
        "accessibility",
        "for_children",
    ]:

        column_nice = column.replace("_", " ").title()
        column_emoji = amenity_emoji.get(column)
        if column_emoji:
            column_nice = column_emoji + " " + column_nice

        options_highlighted = []

        for suffix in ["include", "exclude", "include_all", "include_any"]:
            key = f"{column}_{suffix}"
            options = params.get(key)
            if options is None:
                continue

            for option in options:
                if "include" in suffix:
                    options_highlighted.append(f":blue-background[{option}]")
                else:
                    options_highlighted.append(f"~~:red-background[{option}]~~")

        if not options_highlighted:
            continue

        line = f"**{column_nice}**: " + ", ".join(options_highlighted)
        lines.append(line)
        lines.append("\n")

    return "\n".join(lines)


def format_header(row):
    lines = []

    flag = country_flags[row["country"]]
    line = flag + " " + row["city"] + " "
    line = line + f"**{row['id']}** ({row['accomodation_type']})"
    lines.append(line)
    lines.append("\n")

    line = (
        f"From **${row['price']}**\n\n"
        f"Rating: **{row['rating']:.1f}** "
        f"({row['rating_count']} total reviews)"
    )
    lines.append(line)
    lines.append("\n")

    return "\n".join(lines)


def format_amenities(row, params):

    lines = []

    for column in [
        "property_amenities",
        "room_amenities",
        "wellness_spa",
        "accessibility",
        "for_children",
    ]:
        options = [o for o in row[column] if o != UNCATEGORIZED]
        column_emoji = amenity_emoji[column]
        column_nice = column_emoji + " " + column.replace("_", " ").title()

        options_highlighted = []
        for option in options:

            param_options = []

            key = f"{column}_include_all"
            include_all_options = params.get(key)
            # key can be explicitly None
            # so we don't do params.get(key, [])
            if include_all_options is not None:
                param_options.extend(include_all_options)

            key = f"{column}_include_any"
            include_any_options = params.get(key)
            if include_any_options is not None:
                param_options.extend(include_any_options)

            if option in param_options:
                options_highlighted.append(f":blue-background[{option}]")
            else:
                options_highlighted.append(option)

        if not options_highlighted:
            continue

        line = f"**{column_nice}**: " + ", ".join(options_highlighted)
        lines.append(line)
        lines.append("\n")

    return "\n".join(lines)
