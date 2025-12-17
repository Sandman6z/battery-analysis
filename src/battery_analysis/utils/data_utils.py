def filter_data(_listPltCharge: list, _listPltVoltage: list, _intTimes=5, _floatSlopeMax=0.2, _floatDifferenceMax=0.05):
    _listPltChargeFiltered = []
    _listPltVoltageFiltered = []
    for _p in range(len(_listPltCharge)):
        _lisPltChargeSingle = _listPltCharge[_p]
        _listPltVoltageSingle = _listPltVoltage[_p]
        _times = _intTimes
        while _times:
            _listPltChargeSingleTemp = [_lisPltChargeSingle[0]]
            _listPltVoltageSingleTemp = [_listPltVoltageSingle[0]]
            for _c in range(1, len(_lisPltChargeSingle)):
                if (_lisPltChargeSingle[_c] - _lisPltChargeSingle[_c - 1]) == 0:
                    slope = _floatSlopeMax
                else:
                    slope = abs((_listPltVoltageSingle[_c] - _listPltVoltageSingle[_c - 1]) / (_lisPltChargeSingle[_c] - _lisPltChargeSingle[_c - 1]))
                if slope >= _floatSlopeMax:
                    pass
                else:
                    if abs(_listPltVoltageSingle[_c] - _listPltVoltageSingle[_c - 1]) >= _floatDifferenceMax:
                        pass
                    else:
                        _listPltChargeSingleTemp.append(_lisPltChargeSingle[_c])
                        _listPltVoltageSingleTemp.append(_listPltVoltageSingle[_c])
            _lisPltChargeSingle = _listPltChargeSingleTemp
            _listPltVoltageSingle = _listPltVoltageSingleTemp
            _times -= 1
        _listPltChargeFiltered.append(_lisPltChargeSingle)
        _listPltVoltageFiltered.append(_listPltVoltageSingle)
    return _listPltChargeFiltered, _listPltVoltageFiltered
