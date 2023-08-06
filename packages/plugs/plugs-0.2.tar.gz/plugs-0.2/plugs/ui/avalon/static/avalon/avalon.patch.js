var avalonscan = avalon.scan;
avalon.scan = function(elem, vmodel) {
    avalonscan.call(this, elem, vmodel);
    if (avalon.config.$init)
        avalon.config.$init();
}
