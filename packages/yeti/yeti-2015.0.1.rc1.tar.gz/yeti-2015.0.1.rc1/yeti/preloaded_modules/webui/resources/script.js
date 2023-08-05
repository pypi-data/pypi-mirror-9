

function onData(data){
    $(".mod-panel").remove()
    for(var i = 0; i < data.modules.length; i++){
        make_mod_panel(data.modules[i])
    }
}

var panel_html = "\
<div class='panel panel-primary mod-panel'>\
    <div class='panel-heading'>\
        <h3 class='panel-title mod-name'></h3>\
    </div>\
    <div class='panel-body'>\
        <p><strong>Module Path: </strong><span class='mod-filename'></span></p>\
        <!--<h4 style='display: inline'><span class='label mod-status'></span></h4>-->\
        <h5><strong>Description:</strong></h5>\
        <p class='mod-description'></p>\
        <div class='fallbacks' hidden>\
            <h4>Module Fallbacks</h4>\
            <table>\
                <tbody class='fallbacks-data'>\
                </tbody>\
            </table>\
        </div>\
        <div class='mod-buttons'>\
            <button style='margin-top: 10px;' class='btn btn-danger btn-reload'>Reload</button>\
            <button style='margin-top: 10px;' class='btn btn-warning btn-unload'>Unload</button>\
        </div>\
    </div>\
</div>\
"

function make_mod_panel(data){
    $("#mod_blocks").append(panel_html)
    mod_panel = $(".mod-panel").last()
    mod_panel.module = data.subsystem
    mod_panel.find(".mod-name").text(data.subsystem)
    mod_panel.find(".mod-filename").text(data.filename)
    mod_panel.find(".mod-description").text(data.description)
    mod_panel.find(".mod-status").text(data.status)
    mod_panel.find(".btn-unload").attr("onclick", "command_unloadmod('" + data.subsystem + "')")
    mod_panel.find(".btn-reload").attr("onclick", "command_reloadmod('" + data.subsystem + "')")
    for(var i = 0; i < data.fallbacks.length; i++){
        html = "<tr>" + data.fallbacks[i] + "</tr>"
        mod_panel.find(".fallbacks-data").append(html)
    }
}

function watch_module(modname){
    var watchingmod = modname
    getData()
}

function load_handler(){
    send_command("load", $("#module_target")[0].value)
}

function command_unloadmod(modname){
    send_command("unload", modname)
}

function command_reloadmod(modname){
    send_command("reload", modname)
}

function command_loadconf(confname){
    send_command("load_config", confname)
}

function send_command(command, target){
    data = { command: command, target: target }
    $.post("/api/command", data, handle_command_response)
    setTimeout(getData, 200);
}

function handle_command_response(json){
    data = jQuery.parseJSON(json)
    if(data.status != 0){
        display_message(data.message, "error")
    }
    else{
       display_message(data.message, "success")
    }
}

var msg_html = "\
<div class='alert dash_alert' role='alert'>\
</div>\
"

var current_msgbox_id = 0
function display_message(message, status){
    $("#msg_bar").append(msg_html)
    msg_box = $(".dash_alert").last()
    msg_box.html(message)
    msg_box.addClass("dash_alert_" + current_msgbox_id)

    if(status == "error"){
        msg_box.addClass("alert-danger")
    }
    else if(status == "warn"){
        msg_box.addClass("alert-warning")
    }
    else if(status == "success"){
        msg_box.addClass("alert-success")
    }
    else{
        msg_box.addClass("alert-primary")
    }

    setTimeout('clear_message(' + current_msgbox_id + ')', 3000)
    current_msgbox_id += 1
    //alert(message)
}

function clear_message(id){
    $(".dash_alert_" + id).remove()
}

function getDataLoop() {
    getData()
    setTimeout(getDataLoop, 3000);
}

function getData(){
    $.getJSON("/api/json", onData)
    .fail(function(){
       display_message("No response from server.", "warn")
    });
}

$(document).ready(function(){
    $("#load_button").click(load_handler)
    $('#module_target').keypress(function (e) {
        if (e.which == 13) {
            load_handler();
            return false;
        }
    });
    setTimeout(getDataLoop, 100);
})