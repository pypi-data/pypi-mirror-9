viewannotations = {}; //view local annotations in editor
viewglobannotations = {}; //view global annotations
annotationfocus = null;
annotatordetails = false; //show annotor details
showoriginal = false; //show originals instead of corrections
hover = null;
globannotationsorder = ['entity','semrole','coreferencechain','su','dependency','sense','pos','lemma','chunk'] //from high to low



function sethover(element) {
    if ((element) && ($(element).hasClass(view))) {
        if (hover) $(".hover").removeClass("hover");
        $(element).addClass("hover");
        hover = element;
        if ($(element).hasClass('focustype')) {
            //colour related elements
            Object.keys(annotations[element.id]).forEach(function(annotationid){
                if ((annotationid != "self") && (annotations[element.id][annotationid].type == annotationfocus.type) && (annotations[element.id][annotationid].set == annotationfocus.set) && (annotations[element.id][annotationid].targets.length > 1)) {
                    annotations[element.id][annotationid].targets.forEach(function(target){
                        $('#' + valid(target)).addClass("hover");
                    });
                }
            });
        }
    }
}


function toggleannotatordetails() {
    annotatordetails = !annotatordetails;
    if (annotatordetails) {
        $('#toggleannotatordetails').addClass("on");
    } else {
        $('#toggleannotatordetails').removeClass("on");
    }
}


function toggleoriginal() {
    showoriginal = !showoriginal;
    if (showoriginal) {
        $('#toggleoriginal').addClass("on");
        Object.keys(annotations).forEach(function(target){
            Object.keys(annotations[target]).forEach(function(annotationkey){
                annotation = annotations[target][annotationkey];
                if ((annotation.annotationid != 'self') && (annotation.type == 'correction') && (annotation.original)) {
                    textblob = "";
                    originalid = "";
                    annotation.original.forEach(function(original){
                        if (original.text) {
                            if ($('#' + valid(target)).hasClass('w')) {
                                $('#' + valid(target) + ' span.lbl').html(original.text);
                            }
                            if (textblob) textblob += " ";
                            textblob += original.text;
                        }
                        if ((original.type == 'w') && (originalid == "")) originalid = original.id;
                    });                        
                    if (annotations[target]['self'].type == 's') {
                        if (annotation.new.length > 0) {
                            if ($('#' + valid(annotation.new[0].id)).hasClass('w')) {
                                $('#' + valid(annotation.new[0].id) + ' span.lbl').html(textblob);
                            }
                        } else {
                            //must be a deletion, show
                            if (annotations[target]['self'].previousword) {
                                //check if the deletion has a colored class
                                var c = '';
                                if (classrank[annotation.class]) {
                                    c = ' class' + classrank[annotation.class];
                                }                                
                                $('#' + valid(annotations[target]['self'].previousword)).after('<div id="'  + originalid + '" class="F w deepest deleted' + c +'"><span class="lbl" style="display: inline;">' + textblob + '&nbsp;</span></div>');
                            }
                        }
                    }

                }
            });
        });
    } else {
        $('#toggleoriginal').removeClass("on");
        window.location.href = ''; //reload page
    }
}

function viewer_onmouseenter(element) {
    sethover(element);
    showinfo(element);
}


function getspantext(annotation) {
    spantext= "";
    annotation.targets.forEach(function(target){
        Object.keys(annotations[target]).forEach(function(annotationid2){
            if (annotationid2 != "self") {
                annotation2 = annotations[target][annotationid2];
                if ((annotation2.type == "t") && (annotation2.class == "current")) {
                    if (spantext) spantext += " ";
                    spantext += annotation2.text;
                }
            }
        });
    });
    return spantext;
}

function getclasslabel_helper(c, key) {
    var label = key;
    c.subclasses.forEach(function(subc){
        if (label != key) return;
        if (subc.id == key) {
            label = subc.label;
            return;
        }
        label = getclasslabel_helper(subc, key);
        if (label != key) return;
    });
    return label;
}

function getclasslabel(set, key) {
    var label = key;
    if (setdefinitions[set]) {
        if (setdefinitions[set].classes[key]) {
            return setdefinitions[set].classes[key].label;
        } else {
            Object.keys(setdefinitions[set].classes).forEach(function(c){
                if (label != key) return;
                label = getclasslabel_helper(setdefinitions[set].classes[c], key);
                if (label != key) return;
            });
        }
    }
    return label;
}

function rendercorrection(correctionid, addlabels) {
    var s = "";
    var correction = corrections[correctionid];
    if ((viewannotations[correction.type+"/"+correction.set])) {
        s = s + "<div class=\"correction\"><span class=\"title\">Correction: " + correction.class + "</span>";
        if (annotatordetails && correction.annotator) {
            s = s + "<br/><span class=\"annotator\">" + correction.annotator + " (" + correction.annotatortype + ")</span>";
            if (correction.datetime) {
                s = s + "<br/><span class=\"datetime\">" + correction.datetime +"</span>";
            }
        }
        if ((correction.suggestions.length > 0) || (correction.original.length > 0)) {
            s = s + "<table>";
        }
        if (correction.suggestions.length > 0) {
            correction.suggestions.forEach(function(suggestion){
                s = s + "<tr><th>Suggestion:</th><td>";
                s = s +  "<div class=\"correctionchild\">";
                s = s +  renderannotation(suggestion,true)
                s = s + "</div></td></tr>";
            });
        }
        if (correction.original.length > 0) {
            correction.original.forEach(function(original){
                if (viewannotations[original.type+"/"+original.set]) {
                    s = s + "<tr><th>Original";
                    if (addlabels) {
                        s = s + " " + getannotationtypename(original.type);
                    }
                    s = s + ":</th><td> ";
                    s = s +  "<div class=\"correctionchild\">";
                    s = s + renderannotation(original,true);
                    s = s + "</div></td></tr>";
                }
            });
        }
        if ((correction.suggestions.length > 0) || (correction.original.length > 0)) {
            s = s + "</table>";
        }
        s = s + "</div>";
    }
    return s;
}

function checkparentincorrection(annotation, correctionid) {
    var parentincorrection = false;
    annotation.targets.forEach(function(t){
        Object.keys(annotations[t]).forEach(function(aid) {
            var a = annotations[t][aid];
            if (aid == 'self') {
                //alert(t + ": '" + a.incorrection + "' vs '" + annotation.incorrection + "'");
                if ((a.incorrection) && (a.incorrection[0] == annotation.incorrection[0]))  {
                    parentincorrection = t;
                }
            }
        });
    });
    return parentincorrection;
}

function getspanroletext(spanroledata) {
    var roletext = "";
    spanroledata.words.forEach(function(wordid){
        if (roletext) roletext += " ";
        roletext += annotations[wordid]['t/undefined:' + textclass].text;
    });
    return roletext;
}

function renderspanrole(spanroledata) {
    return "<br/><label class=\"spanrole\">" + spanroledata.type + ":</label> <span class=\"text\">" + getspanroletext(spanroledata) + "</span>";
}

function renderannotation(annotation, norecurse) {
    //renders the annotation in the details popup
    var s = "";
    if (!((annotation.type == "t") && ((annotation.class == "current")  || (annotation.class == "original")) )) {
        if ((setdefinitions[annotation.set]) && (setdefinitions[annotation.set].type != "open") && (setdefinitions[annotation.set].classes[annotation.class]) ) {
            s = s + "<span class=\"class\">" +  setdefinitions[annotation.set].classes[annotation.class].label + "</span>";
        } else if (annotation.class) {
            s = s + "<span class=\"class\">" + annotation.class + "</span>";
        }
    }
    if (annotation.span) {
        if (spanroles[annotation.type]) {
            spanroles[annotation.type].forEach(function(spanrole){
                annotation.spanroles.forEach(function(spanroledata){
                    if (spanroledata.type == spanrole) {
                        s = s + renderspanrole(spanroledata);
                    }
                });
            });
        } else if (annotation.spanroles.length > 0) {
            annotation.spanroles.forEach(function(spanroledata){
                s = s + renderspanrole(spanroledata);
            });
        }
        if (!spanroles[annotation.type]) {
            spantext = getspantext(annotation);
            s = s + "<br/><span class=\"text\">" + spantext + "</span>";
        }
    }
    if (annotation.type == "t") {
        if (annotation.class != "current") s = s + "<br />";
        s = s + "<span class=\"text\">" + annotation.text + "</span>";
    }
    if (annotatordetails && annotation.annotator) {
        s = s + "<br/><span class=\"annotator\">" + annotation.annotator + " (" + annotation.annotatortype + ")</span>";
        if (annotation.datetime) {
            s = s + "<br/><span class=\"datetime\">" + annotation.datetime +"</span>";
        }
    }
    if ( (annotation.incorrection) && (annotation.incorrection.length > 0) && (!norecurse)) {
        //is this item part of a correction? if so, deal with it
        annotation.incorrection.forEach(function(correctionid){
            //is it really this item or is the entire parent part of the
            //correction? in the latter case we don't want to display a correction
            //here
            if (!checkparentincorrection(annotation, correctionid)) {
                if (corrections[correctionid]) {
                    s = s + rendercorrection( correctionid, true);
                } else {
                    s = s + "<div class=\"correction\"><span class=\"title\">Correction</span></div>";
                }
            }
        });
    }
    return s;
}

function showinfo(element) {
    if ((element) && ($(element).hasClass(view))) {
        if ((element.id)  && (annotations[element.id])) {            
            s = "<div id=\"id\">" + getannotationtypename(annotations[element.id].self.type) + " &bull; " + element.id + " &bull; " + annotations[element.id].self.class + "</div><table>";
            Object.keys(annotations[element.id]).forEach(function(annotationid){
                annotation = annotations[element.id][annotationid];
                if (annotationid != "self") {
                    if ((viewannotations[annotation.type+"/" + annotation.set]) && (annotation.type != "correction")) { //corrections get special treatment
                        label = getannotationtypename(annotation.type);
                        if (annotation.set) {
                            setname = annotation.set;
                        } else {
                            setname = "";
                        }
                        if (setname == "undefined") setname = "";
                        s = s + "<tr><th>" + label + "<br /><span class=\"setname\">" + setname + "</span></th><td>";
                        s = s + renderannotation(annotation);
                        s = s + "</td></tr>";
                    }
                }
            });
            s = s + "</table>";
            if (annotations[element.id].self.incorrection) {
                annotations[element.id].self.incorrection.forEach(function(correctionid){
                    s = s + rendercorrection( correctionid, true);
                });
            }
            $('#info').html(s);
            $('#info').css({'display': 'block', 'top':mouseY+ 20, 'left':mouseX} );
            $('#info').show();    
        }
    }
}


function toggleannotationview(annotationtype, set) {
    viewannotations[annotationtype+"/"+set] = !viewannotations[annotationtype+"/"+set];
    if (viewannotations[annotationtype+"/" + set]) {
        $('#annotationtypeview_' + annotationtype + "_" + hash(set)).addClass('on');
    } else {
        $('#annotationtypeview_' + annotationtype + "_" + hash(set)).removeClass('on');
    }
}


function toggleglobannotationview(annotationtype, set) {
    viewglobannotations[annotationtype+"/"+set] = !viewglobannotations[annotationtype+"/"+set];
    if (viewglobannotations[annotationtype+"/" + set]) {
        $('#globannotationtypeview_' + annotationtype + "_" + hash(set)).addClass('on');
    } else {
        $('#globannotationtypeview_' + annotationtype + "_" + hash(set)).removeClass('on');
    }
    $('span.ab').css('display','none'); 
    $('span.ab').html("");
    renderglobannotations(annotations);
}

function resetglobannotationview() {
    $('#globannotationsviewmenu li').removeClass('on');
    viewglobannotations = {}
    $('span.ab').css('display','none'); 
    $('span.ab').html("");
    renderglobannotations(annotations);
}


function setannotationfocus(t,set) {
    if (annotationfocus) {
        $('.focustype').removeClass("focustype");
        $('#annotationsfocusmenu li').removeClass('on');
        removeclasscolors();
    }
    if (t && set) {
        annotationfocus = { 'type': t, 'set': set };
        $('#annotationtypefocus_' + annotationfocus.type + "_" + hash(annotationfocus.set)).addClass('on');
        Object.keys(annotations).forEach(function(target){
            Object.keys(annotations[target]).forEach(function(annotationkey){
                annotation = annotations[target][annotationkey];
                if ((annotation.type == annotationfocus.type) && (annotation.set == annotationfocus.set)) {
                    if ($('#' + valid(target)).hasClass('w')) {
                        $('#' + valid(target)).addClass("focustype");
                    }
                }
            });
        });
        if (annotationfocus.type != 't') {
            setclasscolors();
        } else {
            $('.focustype').addClass('undofocustype');
        }
    } else {
        annotationfocus = null;
    }
}

function removeclasscolors(toggle) {
    for (var i = 1; i < 8; i++) {
        $('.class' + i).removeClass('class' + i);
    }
    $('.focustype').removeClass('focustype');
    $('.undofocustype').removeClass('undofocustype');
    if (toggle) {
        s = "<span class=\"title\">Legend</span>"; //text for legend
        s = s + "(<a href=\"javascript:setannotationfocus('"+ annotationfocus.type +"','" + annotationfocus.set + "')\">Show</a>)<br />";
        $('#legend').html(s);
    } else {
        $('#legend').hide();
    }
}

function setclasscolors() {
    //count class distribution
    classfreq = {};
    var legendtitle = "";
    var legendtype = "";
    var legendset = "";
    Object.keys(annotations).forEach(function(target){
        Object.keys(annotations[target]).forEach(function(annotationkey){
            annotation = annotations[target][annotationkey];
            if ((annotation.type == annotationfocus.type) && (annotation.set == annotationfocus.set) && (annotation.class)) {
                if (classfreq[annotation.class]) {
                    classfreq[annotation.class]--; //reverse for sorting later
                } else {
                    classfreq[annotation.class] = -1; //reverse for sorting later
                }


                legendtype = annotation.type;
                legendset = annotation.set;
                if (legendtitle == "") {
                    if (annotationtypenames[legendtype]) {
                        legendtitle = annotationtypenames[legendtype];
                    } else {
                        legendtitle = annotation.type;
                    }
                }
            }
        });
    });

    s = "<span class=\"title\">Legend &bull; " + legendtitle + "</span>"; //text for legend
    s = s + "(<a href=\"javascript:removeclasscolors(true)\">Hide</a>)<br />";
    classrank = {}
    currentrank = 1;
    bySortedValue(classfreq, function(key, val){
        if (currentrank < 8) {
            classrank[key] = currentrank;
            var keylabel = getclasslabel(legendset, key);
            s = s + "<div id=\"class" + currentrank + "legend\" class=\"colorbox\"></div><span>" + keylabel + "</span><br />"
            currentrank++;
        }
    });


    Object.keys(annotations).forEach(function(target){
        Object.keys(annotations[target]).forEach(function(annotationkey){
            annotation = annotations[target][annotationkey];
            if ((annotation.type == annotationfocus.type) && (annotation.set == annotationfocus.set) && (annotation.class)) {
                if (classrank[annotation.class]) {
                    if ($('#' + valid(target)).hasClass('w')) {
                        $('#' + valid(target)).addClass('class' + classrank[annotation.class]);
                    }
                    if (($('#' + valid(target)).hasClass('s')) && (annotation.type == 'correction')) {
                        if (annotation.new.length == 0) {
                            //a deletion occurred
                        } else {
                            annotation.new.forEach(function(newtarget) {
                                if (newtarget.type == 'w') {
                                    $('#' + valid(newtarget.id)).addClass('class' + classrank[annotation.class]);
                                }
                            });
                        }
                    }
                }
            }
        });
    });

    $('#legend').html(s);
    $('#legend').show();
}


function partofspanhead(annotation, target) {
    var partofhead = false;
    annotation.spanroles.forEach(function(spanroledata) {
        if (spanroledata.type == "hd") {
            if (spanroledata.words.indexOf(target) != -1) {
                partofhead = true;
            }
        }
    });
    return partofhead;
}


function renderglobannotations(annotations) {
    //annotations are passed so we can work either locally or globally
    //
    var globalannotations = 0;
    Object.keys(viewglobannotations).forEach(function(annotationtypeset){
      if (viewglobannotations[annotationtypeset]) globalannotations += 1;
    });

    if (globalannotations) {
        var containers = {}
        Object.keys(annotations).forEach(function(target){
            var targetabselection = $('#' + valid(target) + " span.ab");
            targetabselection.css('display','none'); //we clear on this level 
            targetabselection.html("");
            var changed = false;
            $(globannotationsorder).each(function(annotationtype){ //ensure we insert types in the desired order
                annotationtype = globannotationsorder[annotationtype];
                Object.keys(annotations[target]).forEach(function(annotationkey){
                    if (annotationkey != "self") {
                        var annotation = annotations[target][annotationkey];
                        if ((annotation.type == annotationtype) && (viewglobannotations[annotation.type + '/' + annotation.set])) {
                                changed = true;
                                var s = "";
                                if (annotation.class) {
                                    s = "<span class=\""+annotation.type+"\">" + annotation.class + "</span>";
                                } else {
                                    s = "<span class=\""+annotation.type+"\">?</span>";
                                }
                                if (annotation.span) {
                                        var extra = "";
                                        var usecontext = true;
                                        if (annotation.type == "dependency") {
                                            //for dependencies we point from the dependents to the head.
                
                                            //grab the head
                                            var headtext = "";
                                            var partofhead = partofspanhead(annotation, target);
                                            annotation.spanroles.forEach(function(spanroledata) {
                                                if (spanroledata.type == "hd") {
                                                    headtext = getspanroletext(spanroledata);
                                                }
                                            });
                                            if (partofhead) { //if we're part of the head, we don't render this annotation here
                                                usecontext = false;
                                                s = "<span class=\""+annotation.type+"\">HD&Leftarrow;" + annotation.class + "</span>";
                                            } else {
                                                extra = "&Rightarrow;<span class=\"headtext\">" + headtext + "</span>";
                                            }
                                        }

                                        if (usecontext) {
                                            var previnspan = false;
                                            var nextinspan = false;
                                            //If the previous word is in the same
                                            //span we do not repeat it explicitly
                                            //but draw a line
                                            var prevwordid = annotations[target]['self']['previousword'];
                                            if ((annotations[prevwordid]) && (annotations[prevwordid][annotationkey])) {
                                                var prevannotation = annotations[prevwordid][annotationkey];
                                                if ((prevannotation.class == annotation.class) && (prevannotation.layerparent == annotation.layerparent)) {
                                                    //previous word part of span already
                                                    if ((annotation.type != "dependency") || (!partofspanhead(prevannotation, prevwordid))) { //for dependencies we're only interested in dependents
                                                        previnspan = true;
                                                    }
                                                }
                                            }

                                            //is the next word still part of the span?
                                            var nextwordid = annotations[target]['self']['nextword'];
                                            if ((annotations[nextwordid]) && (annotations[nextwordid][annotationkey])) {
                                                var nextannotation = annotations[nextwordid][annotationkey];
                                                if ((nextannotation.class == annotation.class) && (nextannotation.layerparent == annotation.layerparent)) {
                                                    if ((annotation.type != "dependency") || (!partofspanhead(nextannotation, nextwordid))) { //for dependencies we're only interested in dependents
                                                        nextinspan = true;
                                                    }
                                                }
                                            }

                                            if ((previnspan) && (nextinspan)) {
                                                s = "<span class=\""+annotation.type+"\" style=\"text-align: center\">&horbar;</span>";
                                            } else if (nextinspan) {
                                                s = "<span class=\""+annotation.type+"\">&lang;" + annotation.class + extra + "</span>";
                                            } else if (previnspan) {
                                                s = "<span class=\""+annotation.type+"\" style=\"text-align: right\">&horbar;&rang;</span>";
                                            } else {
                                                s = "<span class=\""+annotation.type+"\">&lang;" + annotation.class + extra + "&rang;</span>";
                                            }
                                        }


                                        //this is a complex annotatation that
                                        //may span multiple lines, build a
                                        //container for it. All containers will
                                        //have the same height so content can
                                        //be aligned.
                                        var scope = annotation.layerparent 
                                        var containerkey = annotation.type + "/" + annotation.set + "/" + annotation.layerparent;
                                        if (!containers[containerkey]) {
                                            containers[containerkey] = {};
                                        }
                                        var container = null;
                                        if (containers[containerkey][target]) {
                                            container = containers[containerkey][target];
                                        } else {
                                            containers[containerkey][target] = [];
                                        }
                                        if (container === null) {
                                            /* add a container first */
                                            targetabselection.append("<span class=\"abc\">" + s + "</span>");
                                            var abcs = $('#' + valid(target) + " span.ab span.abc")
                                            container = abcs[abcs.length-1]; //nasty patch cause I can't get last() to work
                                        } else {
                                            $(container).append(s);
                                        }
                                        containers[containerkey][target].push(container);
                                } else {
                                    targetabselection.append(s)
                                }
                        }
                    }
                }); ///
            });
            if (changed) targetabselection.css('display','block'); 
        });

        //process containers, all containers for the same span layer must all have the same height (will be set to the height of the largest)
        Object.keys(containers).forEach(function(containerkey){
            var height = 0;
            Object.keys(containers[containerkey]).forEach(function(target){
                containers[containerkey][target].forEach(function(container){
                    c_height =  $(container).height()
                    if (c_height > height) height = c_height;
                });
            });
            if (height > 0) {
                Object.keys(containers[containerkey]).forEach(function(target){
                    containers[containerkey][target].forEach(function(container){
                        $(container).css('height',height);
                    });
                });
            }
        });

    }

}

function viewer_onloadannotations(annotationlist) {
    if (annotationfocus) {
        setclasscolors();
    }
}


function viewer_onupdate() {
    view = 'deepest';
    $('div.F span.lbl').hide();
    if (perspective != "s") {
        $('div.s').css('display', 'inline');
    } else {
        $('div.s').css('display', 'block');
    }
    $('div.persp').removeClass('persp');
    if ((perspective) && (perspective != "document") && ((!perspective_ids) || (perspective_ids.length > 1))) {
        $('div.' + perspective).addClass('persp');
    }
    //$('ul#viewsmenu li').removeClass('on');
    //view=deepest
    $('div.deepest>span.lbl').show();
    //$('li#views_deepest').addClass('on');
    /*
    } else if (v == 'w') {
        $('div.w>span.lbl').show();
        $('li#views_w').addClass('on');
    } else if (v == 's') {
        $('div.s').css('display', 'block');
        $('div.s>span.lbl').show();
        $('li#views_s').addClass('on');
    } else if (v == 'p') {
        $('div.p>span.lbl').show();
        $('li#views_p').addClass('on');
    }
    */
}

function viewer_ontimer() {
    if (namespace != "testflat") { //no polling for tests 
       $.ajax({
            type: 'GET',
            headers: {'X-sessionid': sid },
            url: "/viewer/" + namespace + "/"+ docid + "/poll/",
            success: function(data) {
                update(data);
            },
            dataType: "json"
        }); 
    }
}



function viewer_loadmenus() {
    s = "";
    s2 = "<li><a href=\"javascript:setannotationfocus()\">Clear</li>";
    sglob = "<li><a href=\"javascript:resetglobannotationview()\">Clear</li>";
    Object.keys(declarations).forEach(function(annotationtype){
      Object.keys(declarations[annotationtype]).forEach(function(set){
        if ((configuration.allowedviewannotations === true) || (configuration.allowedviewannotations.indexOf(annotationtype + '/' + set) != -1) || (configuration.allowedviewannotations.indexOf(annotationtype) != -1)) {
            var state = "";
            if ((configuration.initialviewannotations === true) || (configuration.initialviewannotations.indexOf(annotationtype + '/' + set) != -1) || (configuration.initialviewannotations.indexOf(annotationtype) != -1)) {
                viewannotations[annotationtype + "/" + set] = true;
                state = "class=\"on\"";
            } else {
                state = "";
            }
            label = getannotationtypename(annotationtype);
            s = s +  "<li id=\"annotationtypeview_" +annotationtype+"_" + hash(set) + "\" " + state + "><a href=\"javascript:toggleannotationview('" + annotationtype + "', '" + set + "')\">" + label + "<span class=\"setname\">" + set + "</span></a></li>";
            if (globannotationsorder.indexOf(annotationtype) != -1) {
                if (('initialglobviewannotations' in configuration  ) &&  ((configuration.initialglobviewannotations === true) || (configuration.initialglobviewannotations.indexOf(annotationtype + '/' + set) != -1) || (configuration.initialglobviewannotations.indexOf(annotationtype) != -1))) {
                    globviewannotations[annotationtype + "/" + set] = true;
                    state = "class=\"on\"";
                } else {
                    state = "";
                }
                sglob = sglob +  "<li id=\"globannotationtypeview_" +annotationtype+"_" + hash(set) + "\" " + state + "><a href=\"javascript:toggleglobannotationview('" + annotationtype + "', '" + set + "')\">" + label + "<span class=\"setname\">" + set + "</span></a></li>";
            }
        }
        if ((configuration.allowedannotationfocus === true) || (configuration.allowedannotationfocus.indexOf(annotationtype + '/' + set) != -1) || (configuration.allowedannotationfocus.indexOf(annotationtype) != -1)) {
            s2 = s2 +  "<li id=\"annotationtypefocus_" +annotationtype+"_" + hash(set) + "\"><a href=\"javascript:setannotationfocus('" + annotationtype + "','" + set + "')\">" + label +  "<span class=\"setname\">" + set + "</span></a></li>";
        }

      });
    });
    $('#annotationsviewmenu').html(s); //TODO: sort alphabetically
    $('#globannotationsviewmenu').html(sglob);
    $('#annotationsfocusmenu').html(s2);
}




function viewer_contentloaded(data) {
    editfields = 0;
    if (textclass != 'current') rendertextclass();
    if (annotationfocus) {
        setannotationfocus(annotationfocus.type, annotationfocus.set);
    }
    renderglobannotations(annotations);
}


function opensearch() {
    $('#search').show();
    $('#search').draggable();
}

function highlight(data) {
    $('.highlighted').removeClass('highlighted');
    if (data.elements) {
        data.elements.forEach(function(returnitem){
            if (returnitem.elementid) { 
                $('#' + valid(returnitem.elementid)).addClass("highlighted");
            }
        });
    }
}


function viewer_oninit() {
    closewait = false; //to notify called we'll handle it ourselves 


    $('#document').mouseleave( function(e) {
        $('#info').hide();
    });  
    annotatordetails = false;
    if ((configuration.annotationfocustype) && (configuration.annotationfocusset)) {
        setannotationfocus(configuration.annotationfocustype, configuration.annotationfocusset);
    }
    viewer_loadmenus();
    loadperspectivemenu();


    //if (viewannotations['t']) toggleannotationview('t');
    $('#document').mouseleave(function() { $('#info').hide(); });

    $('#searchdiscard').click(function(){
        $('#search').hide();
    });

    $('#searchsubmit').click(function(){ 

        var queries = $('#searchqueryinput').val().split("\n"); 
        var changeperspective = $('#searchperspective').is(':checked');

        var format = "flat";
        if (!changeperspective) {
            format = "json"
        }


        for (i = 0; i < queries.length; i++) {
            var cql = false;
            if ((queries[i].trim()[0] == '"') || (queries[i].trim()[0] == '[')) {
                cql = true;
                queries[i] = "USE " + namespace + "/" + docid + " CQL " + queries[i].trim();
            } else if (queries[i].trim().substr(0,3) == "USE") {
                queries[i] = queries[i].trim();
            } else {
                queries[i] = "USE " + namespace + "/" + docid + " " + queries[i].trim();
            }  
            if (queries[i].indexOf('FORMAT') == -1) {
                queries[i] += " FORMAT flat"; 
            }
        }

        $('#wait span.msg').val("Executing search query and obtaining results");
        $('#wait').show();

        $.ajax({
            type: 'POST',
            url: "/" + namespace + "/"+ docid + "/query/",
            contentType: "application/json",
            //processData: false,
            headers: {'X-sessionid': sid },
            data: JSON.stringify( { 'queries': queries}), 
            success: function(data) {
                if (data.error) {
                    $('#wait').hide();
                    alert("Received error from document server: " + data.error);
                } else {
                    $('#search').hide();
                    if (changeperspective) {
                        settextclassselector(data);
                        update(data);
                        if (textclass != 'current') rendertextclass();
                        if (annotationfocus) {
                            setannotationfocus(annotationfocus.type, annotationfocus.set);
                        }
                        renderglobannotations(annotations);
                    } else {
                        highlight(data);
                    }
                    $('#wait').hide();
                }
            },
            error: function(req,err,exception) { 
                $('#wait').hide();
                alert("Query failed: " + err + " " + exception + ": " + req.responseText);
            },
            dataType: "json"
        });
    });
}
