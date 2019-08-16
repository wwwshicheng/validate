# validate
数据验证、格式化

```
def name_parse(d):
    if d == "tom":
        return "tom1"
    return d
    
def addres_parse(d):
    return "abcdefg"



VALIDATE = {
    # 1:课文预习 2 生词听写 3 单元复习 4 高频错题 5 生词听写   6 课外阅读
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
        addres=Schema(addres_parse,  required=True),
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
        schema.error = "作业数据格式错误"
        schema.validate(args.data3)
    except Exception as e:
        print("aaa")
        return fail_response(str(e))
    return ok_response()
    ```