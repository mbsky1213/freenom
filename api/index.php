<?php
/**
 * 入口文件
 * 云函数版本维护：
 * 1、去掉顶部的 “#!/usr/bin/env php”，将文件名改为 index.php
 * 2、将 “define('IS_SCF', false);” 改为 “define('IS_SCF', true);”
 * 3、干掉最下方的 run(); 调用
 */
require '../index.php';
run();