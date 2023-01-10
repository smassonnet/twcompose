from twcompose.compose import TwitterComposeModel


def generate_json_schema():
    print(TwitterComposeModel.schema_json())


if __name__ == "__main__":
    generate_json_schema()
