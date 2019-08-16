# @File  : views.py
# @Author: wsc
# @Date  : 2019/8/12
# @Desc  :
from libs.common import ok_response, fail_response
from libs.validate import Schema


def name_parse(d):
    if d == "asdasd":
        return 1
    return 2


VALIDATE = {
    1: Schema(typ={"code": str, "value": int}),
    2: Schema(typ={"qid": []}),
    3: Schema(typ={"qid": []}),
    4: Schema(typ={"qid": []}),
    5: Schema(typ={"qid": []}),
    6: Schema(typ={"re_data": [{"re_id": int, "re_name": str}]})
}


def r_validate(request):
    args, err = request.QUERY.argument(
        name=Schema(str, required=True, f=name_parse, error="name 参数异常"),
        age=Schema(int, required=True, f=lambda a: 20 > a > 10),
        date=Schema("date", required=True),
        timestamp=Schema("timestamp", required=True),
        phone=Schema("^1([38]\d|5[0-35-9]|7[3678])\d{8}$", required=True),
        addressssss=Schema(name_parse,  required=True),
        data=Schema([int], required=True),
        data1=Schema({"a": str, "b": [int]}, required=True),
        data2=Schema([{"a": str, "b": [int]}], required=True),
        data3=Schema({})
    )
    if err:
        return fail_response(err)
    try:
        schema = VALIDATE.get(1)
        schema.key = "data3"
        schema.error = "数据格式错误"
        schema.validate(args.data3)
    except TypeError as e:
        return fail_response(str(e))
    return ok_response()
