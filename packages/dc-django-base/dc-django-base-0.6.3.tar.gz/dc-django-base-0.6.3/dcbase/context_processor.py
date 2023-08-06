def base(request):
    return {'dcbase_need_tz_offset': getattr(request, 'needTzOffset', False)}