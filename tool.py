import os
import glob
import json
import uuid

from datetime import datetime
from typing import Optional
from typing import List
from typing import Dict

# Models
from models.settings import settings
from models.recipe import Recipe
from models.output import Output
from models.output import OutputComparison

# Util
from helper.terminal import print_bold

# PATHS
PATH_REVISIONS = settings.PATH_REVISIONS
PATH_RECIPES = settings.PATH_RECIPES


def init_structure() -> None:
    # revisions path
    if not os.path.exists(PATH_REVISIONS):
        print(f"Created: {PATH_REVISIONS}")
        os.makedirs(PATH_REVISIONS)
    else:
        print(f"Path exists: {PATH_REVISIONS}")

    # recipes path
    if not os.path.exists(PATH_RECIPES):
        print(f"Created: {PATH_RECIPES}")
        os.makedirs(PATH_RECIPES)
    else:
        print(f"Path exists: {PATH_RECIPES}")


def show_revision(revision: str, changes: bool) -> None:

    print(changes)

    # try opening file
    try:
        with open(PATH_REVISIONS + "/" + revision + ".json") as json_data:
            data = Output.model_validate_json(json.dumps(json.load(json_data)))

            print_bold("\nRevision:\t" + data.revision.__str__())
            print(f"Previous:\t{data.previous.__str__()}")
            print(f"Created at:\t{data.created}")

            # objects
            if not changes:
                print_bold(f"\nObjects:\t{len(data.current_fields)}\n")
                c: int = 1
                for sfdc_object in data.current_fields:
                    print(
                        f"\t\t[{c}]\t{sfdc_object} ({len(data.current_fields[sfdc_object])})"
                    )
                    c += 1
            elif changes and data.comparison is not None:
                print_bold(f"\nChanges:")

                change_list: List[OutputComparison] = [
                    c
                    for c in data.comparison
                    if len(c.additions) > 0 or len(c.removals) > 0
                ]

                for change in change_list:
                    print_bold(f"\t{change.name}")
                    if len(change.additions) > 0:
                        print(f"\t- Additions:")
                        a: int = 1
                        for addition in change.additions:
                            print(f"\t\t[{a}] {addition}")
                            a += 1
                    if len(change.removals) > 0:
                        print(f"\t- Removals:")
                        r: int = 1
                        for removal in change.removals:
                            print(f"\t\t[{r}] {removal}")
                            r += 1
                    # space
                    print("\n")

    except FileNotFoundError:
        print(f"Unknown revision:\t{revision}")


def show_revisions() -> None:
    chain: List[uuid.UUID] = []
    revision_chain: List[Output] = []

    # find all revisionsi
    for filename in glob.glob(os.path.join(PATH_REVISIONS, "*.json")):
        # validate revision file
        with open(filename) as json_data:
            data = Output.model_validate_json((json.dumps(json.load(json_data))))
            json_data.close()

            if len(chain) == 0 or data.previous is None:
                chain.append(data.revision)
                revision_chain.append(data)
            else:
                if data.previous:
                    if data.previous in chain:
                        # get position
                        position: int = chain.index(data.previous)
                        chain.insert(position + 1, data.revision)
                        revision_chain.insert(position + 1, data)

    i: int = 1

    print_bold("Revisions:")
    for element in revision_chain:
        if element.previous is not None:
            print(
                f"[{i}] \t {element.created} \t {element.revision} \t <- {element.previous}"
            )

        else:
            print(f"[{i}] \t {element.created} \t {element.revision}")
        i += 1


def fields_from_recipe(recipe: Recipe) -> Dict[str, List[str]]:

    output: Dict[str, List[str]] = {}

    for node in recipe.nodes:
        this_node = recipe.nodes[node]

        if this_node.action == "load":
            parameters = this_node.parameters

            if (
                parameters.dataset is not None
                and parameters.dataset.type == "connectedDataset"
            ):
                object_name = parameters.dataset.label

                if parameters.fields is not None:
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

        if data is not None:
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
            p_comparison: OutputComparison = OutputComparison(name=previous_name)
            p_comparison.removals = previous[previous_name]

            comparisons.append(p_comparison)

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

        if previous_recipe is not None:
            output.comparison = perform_comparison(data, previous_recipe.current_fields)

    # save to file
    with open(
        PATH_REVISIONS + "/" + output.revision.__str__() + ".json",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(output.model_dump_json(indent=4))

    print("Created Revision:\t" + output.revision.__str__())


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
