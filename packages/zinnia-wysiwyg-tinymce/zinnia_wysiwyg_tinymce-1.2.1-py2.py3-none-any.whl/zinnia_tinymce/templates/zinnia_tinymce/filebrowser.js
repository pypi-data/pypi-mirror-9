function mce_filebrowser(field_name, url, type, win) {
    tinyMCE.activeEditor.windowManager.open({
        url: "{% url "tinymce-filebrowser-dispatch" %}" + type + "/",
        width: 400,
        height: 400,
        movable: true,
        inline: true,
        close_previous: "no"
    }, {
        window : win,
        input : field_name
    });
}
