from pathlib import Path
from mlrun import code_to_function
import yaml

if __name__ == "__main__":
    for function_dir in map(lambda p: p.parent.absolute(), Path().glob("*/function.yaml")):
        item_yaml = function_dir / "item.yaml"

        item = yaml.load(open(item_yaml, "r"))

        code_to_function(
            name=item["name"],
            project="",
            tag=item["version"],
            filename=item["spec"]["filename"],
            handler=item["spec"]["handler"],
            kind=item["spec"]["kind"],
            image=item["spec"].get("image"),
            code_output=f"{item['name']}.py",
            embed_code=True,
            description=item["description"],
            requirements=item["spec"]["requirements"] or None,
            categories=item["categories"] or None,
            labels=item["labels"] or None,
            with_doc=True
        )
