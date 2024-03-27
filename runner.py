import os
import glob
import json
import uuid
from datetime import datetime
from typing import Optional
from typing import List
from typing import Dict

# Models
from models.recipe import Recipe
from models.output import Output
from models.output import OutputComparison

# PATHS
PATH_REVISIONS = "revisions"
PATH_RECIPES = "recipes"


def init_structure():
    # revisions path
    if not os.path.exists(PATH_REVISIONS):
        os.makedirs(PATH_REVISIONS)
    # recipes path
    if not os.path.exists(PATH_RECIPES):
        os.makedirs(PATH_RECIPES)


def fields_from_recipe(recipe: Recipe) -> Dict[str, List[str]]:

    output: Dict[str, List[str]] = {}

    for node in recipe.nodes:
        this_node = recipe.nodes[node]

        if this_node.action == "load":
            parameters = this_node.parameters

            if parameters.dataset.type == "connectedDataset":
                object_name = parameters.dataset.label

                # object already available, check fields
                if object_name in output:
                    for par in parameters.fields:
                        if par not in output[object_name]:
                            output[object_name].append(par)
                else:
                    output[object_name] = parameters.fields

    return output


def load_recipe_json(path: str) -> Recipe | None:
    try:
        with open(path) as json_data:
            return Recipe.model_validate_json(json.dumps(json.load(json_data)))
    except Exception as e:
        print(e)
        return None


def load_revision(path: str) -> Output | None:
    try:
        with open(path) as json_data:
            return Output.model_validate_json(json.dumps(json.load(json_data)))
    except Exception as e:
        print(e)
        return None


def combine_output(
    output: Dict[str, List[str]], new: Dict[str, List[str]]
) -> Dict[str, List[str]]:

    for key in new.keys():
        # key combination
        if key not in output.keys():
            output[key] = []

        # list combination
        for field in new[key]:
            if field not in output[key]:
                output[key].append(field)

    return output


def extract_recipe_json(previous: Optional[uuid.UUID] = None):

    output: Dict[str, List[str]] = {}

    for filename in glob.glob(os.path.join(PATH_RECIPES, "*.wdpr")):
        data = load_recipe_json(filename)
        output = combine_output(output, fields_from_recipe(data))

    # save to file
    save_revision(output, previous)


def perform_comparison(
    current: Dict[str, List[str]], previous: Dict[str, List[str]]
) -> List[OutputComparison]:

    comparisons: List[OutputComparison] = []

    # current vs. previous
    # can find additions or removals of objects that are currently
    # present could have been present before
    for current_name in current.keys():

        c: OutputComparison = OutputComparison(name=current_name)

        # object not in previous => all are additions
        if current_name not in previous.keys():
            c.additions = current[current_name]
        # object in previous
        else:
            ## find additions
            c.additions = list(set(current[current_name]) - set(previous[current_name]))
            ## find removals
            c.removals = list(set(previous[current_name]) - set(current[current_name]))

        comparisons.append(c)

    # previous vs. current
    # would only find removals, if the object was there before
    # but is not present anymore
    for previous_name in previous.keys():
        if previous_name not in current.keys():
            c: OutputComparison = OutputComparison(name=previous_name)
            c.removals = previous[previous_name]

            comparisons.append(c)

    return comparisons


def save_revision(data: Dict[str, List[str]], previous: Optional[uuid.UUID] = None):

    output = Output(
        revision=uuid.uuid4(),
        previous=previous,
        created=datetime.now().isoformat(),
        current_fields=data,
    )

    # make comparison, if required
    if previous is not None:
        previous_recipe = load_revision(
            PATH_REVISIONS + "/" + previous.__str__() + ".json"
        )
        output.comparison = perform_comparison(data, previous_recipe.current_fields)

    # save to file
    with open(
        PATH_REVISIONS + "/" + output.revision.__str__() + ".json",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(output.model_dump_json(indent=4))

    print("Created Revision: " + output.revision.__str__())


def find_previous() -> Optional[uuid.UUID]:

    chain: List[uuid.UUID] = []

    # load all files from revision
    for filename in glob.glob(os.path.join(PATH_REVISIONS, "*.json")):
        with open(filename) as json_data:
            data = Output.model_validate_json(json.dumps(json.load(json_data)))
            json_data.close()

            # if chain is empty, just add first one
            if len(chain) == 0:
                chain.append(data.revision)
            else:
                # check if there is a previous to add
                if data.previous:
                    # check if the previous is in list and find position
                    if data.previous in chain:
                        # get position
                        position: int = chain.index(data.previous)
                        # add current revision after the previous ones position
                        chain.insert(position + 1, data.revision)

    if len(chain) > 0:
        return chain[len(chain) - 1]
    else:
        return None


def main():
    print("-- running main")

    previous = find_previous()

    extract_recipe_json(previous)


if __name__ == "__main__":
    # check and initialize folder structure
    init_structure()

    # run comparison
    main()
