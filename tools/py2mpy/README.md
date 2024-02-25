### PY to MPY 说明

 **默认转lib文件，生成lib_mpy** 
```
cd micropython/micropython_dhzm/tools/py2mpy/

make

make clean
```
 **转xx文件，生成xx_mpy** 
```
cd micropython/micropython_dhzm/tools/py2mpy/

make PY_LIB=xx
make PY_LIB=xx clean
```