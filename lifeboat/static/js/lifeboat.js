/**
 * Created by boredom23309 on 12/16/15.
 */

var entityMap = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': '&quot;',
    "'": '&#39;',
    "/": '&#x2F;'
};

function escapeHtml(string) {
    return String(string).replace(/[&<>"'\/]/g, function (s) {
        return entityMap[s];
    });
}


var orig_destination_html = '<input id="id_destination" maxlength="200" name="destination" type="text">';

    var rescue_type_selector = $("#id_type");
    rescue_type_selector.on("change", function(event){
        var value = event.target.value;
        var destination_field = $("#id_destination");
        var dest_html = "";
        if(value == "callback"){
            dest_html = "<select id='id_destination' name='destination'>";
            for(var choice in callback_rescue_destination_choices){
                if(!callback_rescue_destination_choices.hasOwnProperty(choice))continue;
                dest_html += "<option value='" + choice + "'>" + callback_rescue_destination_choices[choice] + "</option>";
            }
            dest_html += "</select>"
        }else{
            dest_html = orig_destination_html;
        }
        destination_field.parent().html(dest_html);
    });

    function get_error_buckets(ets){
        var buckets = {};
        for(var i = 0; i < ets["errors"].length; i++){
            var p = ets["errors"][i]["received_pieces"];
            var date = new Date(p[0], p[1], p[2], p[3], p[4], p[5]);
            var key = p[0].toString() +  p[1].toString() +  p[2].toString() +  p[3].toString();
            ets["errors"][i]["date"] = date;
            if(!buckets.hasOwnProperty(key)){
                buckets[key] = {
                    "date": date,
                    "date_pieces": p,
                    "date_label": make_haxis_label(date),
                    "errors": [ets["errors"][i]]
                }
            }else{
                buckets[key]["errors"].push(ets["errors"][i]);
            }
        }
        return buckets

    }

    function update_module_info(data){
        error_table_state["errors"] = data["errors"];
        draw_module_histogram(error_table_state);
    }

    /*
    function draw_module_timeline(){
        var data = new google.visualization.DataTable();
        data.addColumn("datetime", "Occurred");
        data.addColumn("number", "Errors");
        //data.addColumn("string", "text1");
        //data.addColumn("string", "text2");
        var buckets = get_error_buckets();
        var rows = [];
        for(var key in buckets){
            if(!buckets.hasOwnProperty(key)){
                continue;
            }
            var b = buckets[key];
            var errors = "";
            for(var i = 0; i < b[1].length; i++){
                errors += "<a href='#'>Test<\a><br />";
            }
            rows.push([b[0], b[1].length]);
        }
        data.addRows(rows);
        var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('chart_div'));
        chart.draw(data, {height: 450, displayAnnotations: true});
    }

    // Due to bug in google charts API, it is unable to produce a histogram with independent variable of dates.
    //

    function draw_module_histogram(){
        var data_as_array = [["Exception", "Date Received"]];
        for(var i = 0; i < error_table_state["errors"].length; i++) {
            var p = error_table_state["errors"][i]["received_pieces"];
            var date = new Date(p[0], p[1], p[2], p[3], p[4], p[5]);
            data_as_array.push([error_table_state["errors"][i]["exception"], date]);
        }
        console.log(data_as_array);
        var data = google.visualization.arrayToDataTable(data_as_array);
        var options = {
            legend: { position: 'none' },
        };

        var chart = new google.visualization.Histogram(document.getElementById('chart_div'));
        chart.draw(data, options);
    } */

    function make_haxis_label(datetime){
        var date = datetime.getFullYear().toString() + "/" + (datetime.getMonth()+1).toString() + "/" + datetime.getDate();
        var time = "";
        if(datetime.getHours() < 12){
            time = (datetime.getHours() == 12 ? 12 : datetime.getHours() % 12).toString() + " AM"
        }else{
            time = (datetime.getHours() == 12 ? 12 : datetime.getHours() % 12).toString() + " PM"
        }

        return date + " " + time;
    }



    function fetch_errors(cb){
        var data = {
            "sort_by": error_table_state["sort_by"].join(','),
            "page": error_table_state["page"],
            "page_size": error_table_state["page_size"],
            "module_id": error_table_state["module_id"],
            "search_term": error_table_state["search_term"],
        };
        $.get(errors_url, data, cb, "json");

    }

    function update_page_numbers(){
        var page_numbers = $("#error-summary-table-page-numbers");
        var html = "";
        var desired_pages = 5;
        var start_page = 1;
        var min_page_diff_from_current = 2;


        var current_page = error_table_state["current_page"];
        var stop_page = current_page + min_page_diff_from_current;
        var last_page = error_table_state["last_page"];
        if(current_page - start_page > min_page_diff_from_current){
            start_page = current_page - min_page_diff_from_current;
        }
        if(stop_page - current_page > min_page_diff_from_current){
            stop_page = current_page + min_page_diff_from_current;
        }
        if(stop_page < desired_pages){
            stop_page = desired_pages;
        }
        if(stop_page > last_page){
            stop_page = last_page;
        }
        if(last_page <= desired_pages ){
            start_page = 1;
        }


        if (current_page == 1){
            html += '<li class="disabled"><a href="#">«</a></li>';
        }else{
            html += '<li><a class="active get_page" id="page_number_' + (current_page - 1).toString() + '">«</a></li>';
        }
        if(start_page > 1){
            html += '<li><a class="page_search_button" href="#">...</a></li>';
        }
        for(var i = start_page; i <= stop_page; i++) {
            if (i == current_page) {
                html += '<li class="disabled" ><a class="disabled get_page" id="page_number_' + i.toString() + '">' + i.toString() + '</a></li>';
            } else {
                html += '<li><a class="active get_page" id="page_number_' + i.toString() + '">' + i.toString() + '</a></li>';
            }
        }
        if(stop_page != last_page){
            html += '<li><a class="page_search_button" href="#">...</a></li>';
        }
        if(current_page != last_page) {
            html += '<li><a class="active get_page" id="page_number_' + (current_page + 1).toString() + '">»</a></li>';
        }else{
            html += '<li class="disabled"><a href="#">»</a></li>';
        }

        page_numbers.html(html);
        set_page_number_handlers();

    }

    function fetch_page(page_number){
        error_table_state["page"] = page_number;
        fetch_errors(update_error_table_info);
    }



    function set_error_table_placeholder(state){

        var placeholder_cell = $('#error-summary-table-loading-placeholder-cell');
        var placeholder = $('#error-summary-table-loading-placeholder');

        if(state){
            if(!placeholder.hasClass("spinning")) {
                placeholder.addClass("spinning");
                placeholder_cell.show();
            }
        }else{
            if(placeholder.hasClass("spinning")){
                placeholder.removeClass("spinning").removeClass("hide-row");
                 placeholder_cell.hide();
            }
        }



    }


    function get_id_from_column_id(column_id){
        return column_id.split("_")[1];
    }


    function handle_sort_change(column_id){
        var column = $("#"+column_id);
        var column_name = get_id_from_column_id(column_id);
        if(column.hasClass("sortable_ascending")){
            column.removeClass("sortable_ascending");
            column.addClass("sortable_descending");
            column.children()[0].className = "sort_icon glyphicon glyphicon-arrow-down"
        }else if(column.hasClass("sortable_descending")){
            column.removeClass("sortable_descending")
            column.children()[0].className = "sort_icon"
        }else{
            column.addClass("sortable_ascending");
            column.children()[0].className = "sort_icon glyphicon glyphicon-arrow-up"
        }

        update_error_table_header_and_state(column_name);
    }

    function update_error_table_header_and_state(column_name){
        //allows for multi-column ordering.
        var sortable_columns = $(".sortable");
        var ascending = $(".sortable_ascending");
        var descending = $(".sortable_descending");
        var sort_by = [];
        var name = "";
        var col;
        var i;
        for(i = 0; i < ascending.length; i++){
            col = ascending[i];
            name = get_id_from_column_id(col.id);
            sort_by.push(name);
        }
        for(i = 0; i < descending.length; i++){
            col = descending[i];
            name = get_id_from_column_id(col.id);
            sort_by.push("-" + name);
        }

        error_table_state["sort_by"] = sort_by;
        fetch_errors(update_error_table_info);
    }

    function update_error_table_info(data){
        error_table_state["current_page"] = data["current_page"];
        error_table_state["previous_page"] = data["previous_page"];
        error_table_state["next_page"] = data["next_page"];
        error_table_state["last_page"] = data["last_page"];
        error_table_state["sort_by"] = data["sort_by"];
        error_table_state["errors"] = data["errors"];
        error_table_state["errors_count"] = data["errors_count"];
        error_table_state["failed_errors_count"] = data["failed_errors_count"];
        error_table_state["unhandled_errors_count"] = data["unhandled_errors_count"];
        error_table_state["handled_errors_count"] = data["handled_errors_count"];
        error_table_state["page_size"] = data["page_size"];
        update_error_table_rows();
        update_page_numbers();
        set_view_traceback_handlers();
    }


    function make_error_table_row(e){

        var status_icon = "";
        if(e["status"] == "unhandled"){
            status_icon = '<span class="glyphicon glyphicon-record" title="unhandled" aria-hidden="true"></span>'
        }else if(e["status"] == "handled"){
            status_icon = '<span class="glyphicon glyphicon-ok-circle" title="handled" aria-hidden="true"></span>'
        }else if(e['status'] == "failed"){
            status_icon = '<span class="glyphicon glyphicon-remove-circle" title="failed" aria-hidden="true"></span>'
        }
        var module_info_url = module_info_url_template.replace("00", e["module_id"]);
        var error_info_url = error_link_template.replace("00", e["id"]) + error_link_module;
        var row =  "<tr id='error_" + e["id"] + "'>" +
                "<td>" +
                    status_icon +
                "</td>" +
                "<td>" +
                    '<a class="error_link" href="' + error_info_url + '">' + e["id"] + '</a>' +
                "</td>" +

                "<td class='error_module_name'>" +
                    '<a href="' + module_info_url + '" id="error_module_' + e["module_id"] + '" data-toggle="tooltip" title="'+ e["module"] +'">' + e["module"] + '</a>'+
                "</td>" +
                "<td class='error_exception'>" +
                    e["exception"] +
                "</td>" +
                "<td>" +
                    e["received"] +
                "</td>" +
                "<td style='error_more_info'>" +
                    "<a class='view_tb' id='view_tb_" + e["id"] + "'>view</a>" +
                "</td>" +
                "</tr>";
        return row
    }

    function set_view_tb(id){
        var tb_panel = $("#tb_panel");
        var var_panel = $("#var_panel");
        var error_panel =  $("#error_summary_panel");
        var var_html = "";
        var error = null;
        for (var i = 0; i < error_table_state['errors'].length; i++){
            var e = error_table_state['errors'][i];
            if (id == e["id"]){
                error = e;
                break;
            }
        }
        if(error_table_state["error_being_viewed"] != null && error_table_state["error_being_viewed"] == error["id"]){
            error_table_state["error_being_viewed"] = null;
            error_panel.slideUp();
            return
        }

        error_panel.slideDown();

        $("#error_summary").html("<h4><a href='" + error_link_template.replace("00", e["id"]) + " >" + error["id"] + "</a>  " + error["module"]  + " - " + error["exception"] +   "</h4>" + "<h5>" + error["received"] + "</h5>");
        tb_panel.html("<h4>Traceback:</h4><pre>" + error["traceback"] + "</pre>");
        var_html += "<h4>Variables:</h4><span class='lb_panel'>";
        for(var key in error["vars"]) {

            if (error["vars"].hasOwnProperty(key)) {
                if (error["vars"][key] == null) {
                    var_html += key + ": " + "None" + "<br />";
                } else {
                    var_html += key + ": " + escapeHtml(error["vars"][key]) + "<br />";
                }
            }
        }
        var_panel.html(var_html + "</span>");
        error_table_state["error_being_viewed"] = error["id"];

    }

    function update_error_table_rows(){
        set_error_table_placeholder(true);
        $("#error-summary-table").find("tr:gt(1)").remove();
        if(error_table_state['errors'].length > 0) {
            for (var i = 0; i < error_table_state['errors'].length; i++) {
                var e = error_table_state["errors"][i];
                $("#error-summary-table tr:last").after(make_error_table_row(e));
            }
        }else{
            $("#error-summary-table tr:last").after("<tr><td style='text-align:center;' colspan='6'>No errors found.</td></tr>");
        }
        set_error_table_placeholder(false);
        $('[data-toggle="tooltip"]').tooltip();
    }


    function set_page_number_handlers(){
        var page_numbers = $(".get_page");
        for(var i = 0; i < page_numbers.length; i++) {
            page_numbers[i].addEventListener("click", function (event) {
                var id_pieces = event.target.id.split('_');
                fetch_page(id_pieces[id_pieces.length - 1]);
                event.preventDefault();
            });
        }
    }

    function set_view_traceback_handlers(){
        var view_tbs = $(".view_tb");
        for(var i = 0; i < view_tbs.length; i++){
            view_tbs[i].addEventListener("click", function(event){
                var id_pieces = event.target.id.split('_');
                set_view_tb(id_pieces[id_pieces.length - 1]);
                event.preventDefault();
            });

        }
    }

    function update_progress_bars(){
        var errors_count = parseInt(error_table_state["errors_count"]);
        if(!errors_count) errors_count = 1;
        var handled_bar = $("#handled_bar");
        var unhandled_bar = $("#unhandled_bar");
        var failed_bar = $("#failed_bar");
        var handled_width;
        var unhandled_width;
        var failed_width;

        handled_width = parseFloat(error_table_state["handled_errors_count"])/errors_count * 100.0;
        handled_bar.width(handled_width + "%");
        handled_bar.html("<span>"+ error_table_state["handled_errors_count"] +"</span>");

        unhandled_width = parseFloat(error_table_state["unhandled_errors_count"])/errors_count * 100.0;
        unhandled_bar.width(unhandled_width + "%");
        unhandled_bar.html("<span>"+ error_table_state["unhandled_errors_count"] +"</span>");

        failed_width = parseFloat(error_table_state["failed_errors_count"])/errors_count * 100.0;
        failed_bar.width(failed_width + "%");
        failed_bar.html("<span>"+ error_table_state["failed_errors_count"] +"</span>");
    }

function draw_module_histogram(ets, title){
        var data = new google.visualization.DataTable();
        var rows = [];

        data.addColumn("datetime", "Date Received");
        data.addColumn("number", "Errors");

        var  buckets = get_error_buckets(ets);
        for(var key in buckets){
            if(!buckets.hasOwnProperty(key)){
                continue;
            }
            var b = buckets[key];
            var errors = "";
            rows.push([{v: b["date"], f:b["date_label"]}, b["errors"].length]);
        }

        data.addRows(rows);

        var options = {
            title: title,
            legend: {
                position: "none"
            },
            hAxis: {
              title: 'Time of Day',
              format: 'h:mm a',
              viewWindow: {}
            },
            bar: {
              groupWidth: 20
            }
        };

        if(min_date != null && max_date != null){
            options["hAxis"]["viewWindow"] = {
                min: min_date,
                max: max_date,
            }
        }else if(min_date != null || max_date != null){
            if(min_date != null) {
                 options["hAxis"]["viewWindow"]["min"] = min_date;
            }
            if(max_date != null) {
                 options["hAxis"]["viewWindow"]["max"] = max_date;
            }

        } else{
                options["hAxis"]["viewWindow"] = {}
        }

        var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
        chart.draw(data, options);
    }

var min_date = null;
var max_date = null;


    function update_log_regex(){
        var re_pattern = $("#id_pattern");
        var log_line = $("#regex_log_line");
        var regex_test_output = $("#regex_test_output");

        regex_test_output.highlightRegex();
        regex_test_output.html(log_line.val());

        if(re_pattern.val() != ""){
            var regex = new RegExp (re_pattern.val(), 'g');
            regex_test_output.highlightRegex(regex);
        }
        /*

        //TODO highlight groups.

        var highlighted = $(".highlight");

        var groups_regex = /\(([^()]+)\)/g;
        for (var h in highlighted){
            if(!h.hasAttribute("innerText"))continue;
            var innerText = h.innerText;
        }
        var matches = groups_regex.match(highlighted[0].html());
        console.log(highlighted[0].innerText)
        */
    }

/*
 * Adapted from jQuery Highlight Regex Plugin v0.1.2
 *
 * Based on highlight v3 by Johann Burkard
 * http://johannburkard.de/blog/programming/javascript/highlight-javascript-text-higlighting-jquery-plugin.html
 *
 * (c) 2009-13 Jacob Rothstein
 * MIT license
 */
(function( $ ) {

  var normalize = function( node ) {
    if ( ! ( node && node.childNodes ))
        return;
      var children     = $.makeArray( node.childNodes )
    ,   prevTextNode = null;
    $.each( children, function( i, child ) {
      if ( child.nodeType === 3 ) {
        if ( child.nodeValue === "" ) {
          node.removeChild( child )
        } else if ( prevTextNode !== null ) {
          prevTextNode.nodeValue += child.nodeValue;
          node.removeChild( child )
        } else {
          prevTextNode = child
        }
      } else {
        prevTextNode = null;
        if ( child.childNodes ) {
          normalize( child )
        }
      }
    })
  };

  $.fn.highlightRegex = function( regex, options ) {
    if ( typeof regex === 'object' && !(regex.constructor.name == 'RegExp' || regex instanceof RegExp ) ) {
      options = regex;
      regex = undefined
    }
    if ( typeof options === 'undefined' ) options = {};

    options.className = options.className || 'highlight';
    options.tagType   = options.tagType   || 'span';
    options.attrs     = options.attrs     || {};

    if ( typeof regex === 'undefined' || regex.source === '' ) {
      $( this ).find( options.tagType + '.' + options.className ).each( function() {
        $( this ).replaceWith( $( this ).text() );
        normalize( $( this ).parent().get( 0 ))
      })
    } else {
      $( this ).each( function() {
        var elt = $( this ).get( 0 );
        $.each( $.makeArray( elt.childNodes ), function( i, searchnode ) {
          var spannode, middlebit, middleclone, pos, match, parent
          normalize( searchnode );
          if ( searchnode.nodeType == 3 ) {
            // don't re-highlight the same node over and over
            if ( $(searchnode).parent(options.tagType + '.' + options.className).length ) {
                return;
            }
            while ( searchnode.data && ( pos = searchnode.data.search( regex )) >= 0 ) {
              match = searchnode.data.slice( pos ).match( regex )[ 0 ];
              if ( match.length > 0 ) {
                spannode = document.createElement( options.tagType );
                spannode.className = options.className;
                $(spannode).attr(options.attrs);

                parent      = searchnode.parentNode;
                middlebit   = searchnode.splitText( pos );
                searchnode  = middlebit.splitText( match.length );
                middleclone = middlebit.cloneNode( true );

                spannode.appendChild( middleclone );
                parent.replaceChild( spannode, middlebit )

              } else break
            }
          } else {
            $( searchnode ).highlightRegex( regex, options )
          }
        })
      })
    }
    return $( this )
  }
})( jQuery );

window.setTimeout(function(){
    $("#alert-box").slideUp();
}, 5000);



