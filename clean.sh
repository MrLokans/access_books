#!/bin/bash

array=(C* Java* Разра* PHP Python Ruby* Алгоритмы* Дис* Друг* Информ*)

for item in ${array[*]}
do
    rm -rf ${item}
done
