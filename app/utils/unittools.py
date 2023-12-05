def convert_to_gb(size_value, size_unit):
    if size_unit.lower() == 'kb':
        return size_value / 1024**2
    elif size_unit.lower() == 'mb':
        return size_value / 1024
    elif size_unit.lower() == 'gb':
        return size_value
    elif size_unit.lower() == 'tb':
        return size_value * 1024  # 1 TB = 1024 GB

    return 0


def convert_large_size(size_value, size_unit):
    units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    # 找到给定单位在单位列表中的索引
    current_unit_index = units.index(size_unit)

    # 将大小值不断除以1024，直到小于等于1024为止
    while size_value > 1024 and current_unit_index < len(units) - 1:
        size_value /= 1024
        current_unit_index += 1

    # 返回转换后的值和单位
    return round(size_value, 2), units[current_unit_index]