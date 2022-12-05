import os
import uuid
import boto3
import typing
import logging
from .err.dydb import errorhandler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s"
)
logger = logging.getLogger(__name__)


class DYDB:
    def __init__(
        self,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", None),
        aws_secret_access_key=os.environ.get(
            "AWS_SECRET_ACCESS_KEY", None),
        region_name=os.environ.get("AWS_DEFAULT_REGION", None)
    ):
        self.dydb = boto3.client(
            'dynamodb',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    @errorhandler
    def exists(self, table) -> None:
        self.dydb.describe_table(
            TableName=table
        )

    @errorhandler
    def get(self, table: str, key: typing.Dict) -> typing.Dict:
        return self.dydb.get_item(
            TableName=table,
            Key=self.mapper(key)
        )['Item']

    @errorhandler
    def delete(self, table: str, key: dict) -> None:
        self.dydb.delete_item(
            TableName=table,
            Key=self.mapper(key)
        )

    @errorhandler
    def create(self, table: str, data: typing.Dict) -> None:
        print(self.mapper(data))
        self.dydb.put_item(
            TableName=table,
            Item=self.mapper(data)
        )

    @errorhandler
    def update(self, table: str, key: typing.Dict, data: typing.Dict) -> None:
        """Add if don't have and merge if have (list append not supported yet)"""
        try:
            update_expression, \
                expression_attribute_names, \
                expression_attribute_values = self.__get_update_expressions(
                    data)

            self.dydb.update_item(
                TableName=table,
                Key=self.mapper(key),
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )
        except:
            update_expression, \
                expression_attribute_names, \
                expression_attribute_values = self.__get_update_expressions(
                    data, merge=False)

            self.dydb.update_item(
                TableName=table,
                Key=self.mapper(key),
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
            )

    #
    # Below are utility functions used for AWS DYDB
    #
    def mapper(self, data, include=False):
        if include:
            return self.__mapper(data)
        else:
            return self.__mapper(data)['M']

    def __mapper(self, data: typing.Any) -> typing.Dict:
        """Map dictionary data to DynamoDB-support data scheme recursively"""
        datatype = type(data)
        if datatype == str:
            return {"S": data}
        elif datatype == bool:
            return {"BOOL": data}
        elif datatype == float or datatype == int:
            return {"N": str(data)}
        elif datatype == list:
            return {"L": [self.__mapper(x) for x in data]}
        elif datatype == dict:
            _map = {}
            for k, v in data.items():
                _map[k] = self.__mapper(v)
            return {"M": _map}

    def __flatten(self, data: typing.Dict, sep='.#') -> typing.Dict:
        d = {}
        for k, v in data.items():
            if isinstance(v, dict):
                _d = {sep.join([k, _k]): _v for _k,
                      _v in self.__flatten(v).items()}
                d.update(_d)
            else:
                d[k] = v
        return d

    def __get_update_expressions(self, data: typing.Dict, merge: bool = True):
        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        if merge:
            flattened = self.__flatten(data)
            for i, (k, v) in enumerate(flattened.items()):
                uid = uuid.uuid1().hex
                update_expression += f"{k} = :{uid}"
                if i < len(flattened) - 1:
                    update_expression += ", "
                for sep in k.split("."):
                    if "#" not in sep:
                        continue
                    expression_attribute_names[f"{sep}"] = sep.replace("#", "")
                expression_attribute_values[f":{uid}"] = self.mapper(
                    v, include=True)
        else:
            for i, (k, v) in enumerate(data.items()):
                update_expression += f"#{k} = :{k}"
                if i < len(data) - 1:
                    update_expression += ","
                expression_attribute_names[f"#{k}"] = k
                expression_attribute_values[f":{k}"] = self.mapper(
                    v, include=True)

        return update_expression, expression_attribute_names, expression_attribute_values
