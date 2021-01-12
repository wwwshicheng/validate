# validate
可用于请求参数验证、数据验证等
django 需要对QueryDict扩展下  
[django配置](https://github.com/wwwshicheng/validate/blob/master/validate/middleware.py)
```python
def name_parse(d):
    if d == "tom":
        return "tom1"
    return d
    
def addres_parse(d):
    return "abcdefg"

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
    
Flask暂时这样处理
```python
class BaseView(Resource):
    @staticmethod
    def args():
        """
        获取参数
        """
        query = request.args.copy()
        query.update(request.form)
        try:
            if request.data:
                body = json.loads(request.data.decode())
                query.update(body)
        except JSONDecodeError:
            pass
        return query

    def parameter_casts(self, **kwargs):
        """
        使用方法
        >>> args = self.parameter_casts(keyword=str, page=int, a="(\d+)")
        """
        return casts(self.args(), **kwargs)

    def argument(self, **kwargs):
        """
        使用方法
        >>> args, e = self.argument(
        >>>      name=Schema(type=str, required=True, error="姓名不能为空"),
        >>>      age=Schema(type=int, required=True, filter=lambda x: x > 0, error="年龄信息错误"),
        >>>      image=Schema(type=[str], default=""),
        >>>      data=Schema(type=[{"qid": int, "aid": [str]}])
        >>> )
        """
        args = Struct()
        error = None
        parameter = self.args()
        for k, typ in kwargs.items():
            if not isinstance(typ, Schema):
                raise TypeError()
            v = parameter.get(k)
            try:
                typ.key = k
                args[k] = typ.validate(v)
            except Exception as e:
                error = str(e)
        return args, error
```


