if (IPython.version[0] === '4' && parseInt(IPython.version[2]) >= 2) {
    var path = 'jupyter-js-widgets';
} else {
    var path = 'widgets/js/widget';
    if (IPython.version[0] !== '3') {
        path = 'nbextensions/widgets/' + path;
    }
}

define(['jquery', path ], function($, widget) {
    var IPFileSelector = widget.DOMWidgetView.extend({
        render: function() {
            this.$notebookList = $("<div></div>").addClass("list_container");
            this.buildHeader();

            this.$breadcrumbs = this.$notebookHeader.find('.breadcrumb');

            IPFileSelector.__super__.render.apply(this, arguments);
            var that = this;
            $(this.el).append(this.$notebookList);

            this.model.on('msg:custom', this.handleMsg, this);
            this.home_path = this.model.get('home_path');
            this.selected = { };

            // trigger first change
            this.change_path(this.home_path);
            this.current_path = this.home_path;
            this.current_path_changed();


            this.listenTo(this.model, 'change:current_path', this.current_path_changed, this);
            this.listenTo(this.model, 'change:selected', this.selected_changed, this);
            this.listenTo(this.model, 'change:subfiles', this.refresh_directory, this);
            this.listenTo(this.model, 'change:subdirs', this.refresh_directory, this);
            var msg = { 'type' : 'init' };
            this.send(msg);
        },

        buildRef: function(path) {
            var ref = this.selected;
            var crumbs = this.get_crumbs(path);
            for (var i in crumbs) {
                 if (crumbs[i].length > 0) {
                    if (ref[crumbs[i]] == undefined || ref[crumbs[i]] == true) {
                        ref[crumbs[i]] = { };
                    }
                    ref = ref[crumbs[i]];
                }
            }
            return ref;
        },
        
        selectAll: function(e) {
            var that = e.data.context;
            if (!$(e.target).is("input:checkbox")) {
               var $button = $(e.target).parent("button");
                if ($button.length == 0) {
                    e.target = $(e.target).find('input:checkbox');
                    $(e.target).prop('checked', !$(e.target).prop('checked'));
                }
            }
            var checked = $(e.target).prop('checked');            
            that.dirsChecked = checked;
            that.filesChecked = checked;
            that.selectDirs(checked);
            that.selectFiles(checked);
        },

        selectDirs: function(checked) {
            var ref = this.buildRef(this.current_path);
            for (var i in this.subdirs) {
                var subdir = this.get_last_crumb(this.subdirs[i]);
                if (checked) {
                    ref[subdir] = true;
                } else {
                    delete ref[subdir];
                }
            }
            $("div[data-type='folder'] input:checkbox").prop('checked', checked);
            this.cull_empty(this.selected);
            this.updateSelected();
        },

        selectFiles: function(checked) {
            var ref = this.buildRef(this.current_path);
            for (var i in this.subfiles) {
                var subfile = this.get_last_crumb(this.subfiles[i]);
                if (checked) {
                    ref[subfile] = true;
                } else {
                    delete ref[subfile];
                }
            }
            $("div[data-type='file'] input:checkbox").prop('checked', checked);
            this.cull_empty(this.selected);
            this.updateSelected();
        },
        
        buildHeader: function() {
            this.$notebookHeader = $("<div class='row list_header' style='padding: 0 0 0 0;'></div>");
            var $buttonGroup = $("<div class='btn-group dropdown' style='display: inline-block; margin: 0 0 0 0;'></div>");
            var $selectAll = $("<button title='Select All/None' type='button' class='btn btn-default btn-xs'></button>");
            $selectAll.click({ context : this }, this.selectAll);
            var $selectAllCheck = $("<input type='checkbox' class='pull-left tree-selector'><span>&nbsp;</span></input>");
            $selectAllCheck.appendTo($selectAll);
            $selectAll.appendTo($buttonGroup);
            var $select = $("<button title='Select...' id='ipfs_tree_selector_button' class='btn btn-default btn-xs dropdown-toggle' type='button' data-toggle='dropdown' area-expanded='true'><span class='caret'></span><span class='sr-only'>Toggle Dropdown</span></button>");
            $select.appendTo($buttonGroup);
            var $selectMenu = $("<ul class='dropdown-menu' role='menu' aria-labelledby='ipfs_tree_selector_button'></ul>");
            $($selectMenu).appendTo($buttonGroup);            
            
            var $folders = $("<li role='presentation'><a role='menuitem' tabindex='-1' href='#' title='Select All Folders'><i class='menu_icon folder_icon icon-fixed-width'></i> Folders</a></li");
            $folders.click($.proxy(function() { 
                this.dirsChecked = !this.dirsChecked;
                this.selectDirs(this.dirsChecked);
            }, this));

            var $files = $("<li role='presentation'><a role='menuitem' tabindex='-1' href='#' title='Select All Files'><i class='menu_icon file_icon icon-fixed-width'></i> Files</a></li>");
            $files.click($.proxy(function() {
                this.filesChecked = !this.filesChecked;
                this.selectFiles(this.filesChecked);
            }, this));

            $($folders).appendTo($selectMenu);
            $($files).appendTo($selectMenu);


            this.$notebookHeader.append($buttonGroup);
            this.$notebookHeader.append($("<div style='display: inline-block; margin: 0 0 0 0;'><ul class='breadcrumb' style='margin: 0 0 0 0; padding: 0 0 0 0;'></ul></div>"));
            this.$notebookHeader.appendTo(this.$notebookList);
        },

        handleMsg: function(msg) {
            if (msg['type'] == 'dir_update') {
                this.refresh_directory();
            }
        },

        path_click: function(e) {
            var path = $(this).attr('data-path');
            e.data.context.change_path.apply(e.data.context, [ path ]);
        },

        change_path: function(path) {
            this.model.set("current_path", path);
            this.model.save_changes();
        },

        checkbox_click: function(e) {
            var $container = $(this).parent("div");
            var path = $container.find('a').attr('data-path');
            var checked = $(this).prop('checked');
            var type = $container.parent("div").attr('data-type');
            var that = e.data.context;
            
            var crumbs = that.get_crumbs(path);
            var ref = that.selected;
            if (checked) {
                for (var i in crumbs) {
                    if (i == crumbs.length - 1) {
                        ref[crumbs[i]] = true;
                    } else {
                        if (ref[crumbs[i]] == undefined || ref[crumbs[i]] == true) {
                            ref[crumbs[i]] = { };
                        }
                        ref = ref[crumbs[i]];
                    }
                }
            } else {
                for (var i in crumbs) {
                    if (i == crumbs.length - 1 && ref[crumbs[i]] != undefined) {
                        delete ref[crumbs[i]];
                    } else {
                        if (ref[crumbs[i]] != undefined && ref[crumbs[i]] != true) {
                            ref = ref[crumbs[i]]
                        }
                    }
                }
                that.cull_empty(that.selected);
            }
            that.updateSelected.apply(that);
        },

        cull_empty: function(ref) {
            var keys = Object.keys(ref);
            for (var key in keys) {
                if (ref[keys[key]] != true) {
                    if (Object.keys(ref[keys[key]]).length == 0) {
                        delete ref[keys[key]];
                    } else {
                        this.cull_empty(ref[keys[key]]);
                    }
                }
            }
        },

        selected_changed: function() {
            this.selected = this.model.get('selected');
            this.refresh_directory();
        },

        current_path_changed: function() {
            this.current_path = this.model.get('current_path');
            this.$breadcrumbs.html("");
            this.$home = $("<li><a href='#' data-path='" + this.home_path + "'><i class='fa fa-home'></i></a></li>").appendTo(this.$breadcrumbs);
            var crumbs = this.current_path.substring(this.home_path.length).split('/');
            var crumbpath = this.home_path;
            for (var index in crumbs) {
                if (crumbs[index].length > 0) {
                    crumbpath = crumbpath + "/" + crumbs[index];
                    this.$newrow = $("<li><a href='#' data-path='" + crumbpath + "'>" + crumbs[index] + "</a></li>").appendTo(this.$breadcrumbs);
                }
            }
            this.$breadcrumbs.find("a").click({ context : this }, this.path_click);
        },

        path_selected: function(path) {
            var crumbs = this.get_crumbs(path); 
            var ref = this.selected;
            for (var i in crumbs) {
                if (i == crumbs.length - 1) {
                    return ref[crumbs[i]] != undefined;
                } else {
                    if (ref[crumbs[i]] != undefined) {
                        ref = ref[crumbs[i]];
                    }
                }
            }
            return false;
        },

        get_last_crumb: function(path) {
            var crumbs = this.get_crumbs(path);
            return crumbs[crumbs.length - 1];
        },

        get_crumbs: function(path) {
            return path.substring(this.home_path.length + 1).split('/');
        },

        refresh_directory: function() {
            this.subdirs = this.model.get("subdirs");
            this.subfiles = this.model.get("subfiles");

            this.dirsChecked = false;
            this.filesChecked = false;

            // select all files if parent directory is selected
            var ref = this.model.get('selected');
            this.selected = ref;
            var crumbs = this.get_crumbs(this.current_path);
            var select_all = false;
            for (var i = 0; i < crumbs.length && !select_all && !(ref == undefined || ref == null); i = i + 1) {
                if (ref[crumbs[i]] == true) {
                    select_all = true;
                    ref[crumbs[i]] = { };
                    for (var j in this.subdirs) {
                        var subdir = this.get_last_crumb(this.subdirs[j]);
                        ref[crumbs[i]][subdir] = true;
                    }
                    for (var j in this.subfiles) {
                        var subfile = this.get_last_crumb(this.subfiles[j]);
                        ref[crumbs[i]][subfile] = true;
                    }
                } else {
                    ref = ref[crumbs[i]];
                }
            }
            if (select_all) {
                this.updateSelected();
            }

            // add parent directory link
            $("[data-type='parent']").remove();
            if (this.current_path != this.home_path) {
                var crumbpath = this.home_path;
                for (var i = 0; i < crumbs.length - 1; i = i + 1) {
                    crumbpath = crumbpath + "/" + crumbs[i];
                }
                var $row = $("<div data-type='parent'></div>").addClass("list_item").addClass("row");
                var $container = $("<div class='col-md-12'></div>").appendTo($row);
                var $checkbox = $("<input type='checkbox' style='visibility: hidden;'/>").appendTo($container);
                var $icon = $("<i class='item_icon folder_icon icon-fixed-width'></i>").appendTo($container);
                var $item = $("<a class='item_link' href='#' data-path='" + crumbpath + "'><span class='item_name'>..</span></a>").appendTo($container);
                $item.click({ context : this }, this.path_click);
                $row.prepend($("::before"));
                $row.append($("::after"));
                $row.appendTo(this.$notebookList);
            }

            // add child directories and folders
            $("[data-type='folder']").remove();
            $("[data-type='file']").remove();
            var $current_folders = $("[data-type='folder']");
            var $current_files = $("[data-type='file']");
            for (var i in this.subdirs) {
                var subdir = this.subdirs[i];
                var checked = this.path_selected(subdir);
                var $row = $("<div data-type='folder'></div>").addClass("list_item").addClass("row");
                var $container = $("<div class='col-md-12'></div>").appendTo($row);
                var $checkbox = $("<input type='checkbox' />").appendTo($container);
                $checkbox.click({ context : this }, this.checkbox_click);
                $checkbox.prop('checked', checked);
                var $icon = $("<i class='item_icon folder_icon icon-fixed-width'></i>").appendTo($container);
                var subdir_display = subdir.substring(this.current_path.length + 1) + "/";
                var $item = $("<a class='item_link' href='#' data-path='" + subdir + "'><span class='item_name'>" + subdir_display  + "</span></a>").appendTo($container);
                $item.click({ context : this }, this.path_click);
                $row.prepend($("::before"));
                $row.append($("::after"));
                $row.appendTo(this.$notebookList);
            }
            for (var i in this.subfiles) {
                var subfile = this.subfiles[i];
                var checked = this.path_selected(subfile);
                var $row = $("<div data-type='file'></div>").addClass("list_item").addClass("row");
                var $container = $("<div class='col-md-12'></div>").appendTo($row);
                var $checkbox = $("<input type='checkbox' />").appendTo($container);
                $checkbox.click({ context : this }, this.checkbox_click);
                $checkbox.prop('checked', checked);
                var $icon = $("<i class='item_icon file_icon icon-fixed-width'></i>").appendTo($container);
                subfile_display = subfile.substring(this.current_path.length + 1);
                var $item = $("<a class='item_link' href='#' data-path='" + subfile + "'><span class='item_name'>" + subfile_display  + "</span></a>").appendTo($container);
                $row.prepend($("::before"));
                $row.append($("::after"));
                $row.appendTo(this.$notebookList);
            }
        },
        
        updateSelected: function() {
            var msg = { 'type' : 'select', 'selected' : this.selected };
            this.send(msg);
//            this.model.set('selected', this.selected);
//            this.model.save_changes();
        }
    });

    return {
        IPFileSelector: IPFileSelector
    }
});
