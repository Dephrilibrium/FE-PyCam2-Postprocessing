














def FindXYKeysAboveMinValInMSSCurrents(mssCurrentContainer, minVal:float, onIndicies:range):
    _xyKeys = list(mssCurrentContainer.keys())

    _xyKeysAbove = []
    for _xyKey in _xyKeys:
        _xyInfo = mssCurrentContainer[_xyKey]

        for _i in onIndicies:
            _iVal = _xyInfo[_i]
            if _iVal > minVal:
                _xyKeysAbove.append(_xyKey)
    return _xyKeysAbove