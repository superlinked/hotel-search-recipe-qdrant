import pandas as pd


def load_image_urls(path: str) -> dict:
    return pd.read_json(path, lines=True).set_index("id")["image_src"]


def get_kick_start_options() -> list[str]:
    kick_start_options = [
        "Cheap but highly rated hotels in London, no children",
        "No pets affordable hotel in London",
        "Cheapest hotels in London with free breakfast",
        "Best hotels in Berlin",
    ]
    return kick_start_options


def flatten_response(response: dict) -> list[dict]:
    result = []

    for row in response["results"]:
        obj = {}

        for k, v in row["obj"].items():
            obj[k] = v

        row_flattened = {
            "score": row["entity"]["score"],
            **obj,
        }
        result.append(row_flattened)

    return result


def clean_knn_params(knn_params: dict) -> dict:
    knn_params_clean = {k: v for k, v in knn_params.items() if v is not None}
    keys_remove = [
        "similar_description_weight",
        "limit",
        "radius",
        "natural_query",
        "system_prompt_param",
    ]
    for key in keys_remove:
        knn_params_clean.pop(key, None)
    return knn_params_clean
