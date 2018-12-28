
var tab_add = []
var tab_del = []
var data_select = []
var right = []

function fill_select(){
    td_right = '<td class = "right"><select class="custom-select", id="inputGroupSelect02">'
    for(var i = 0; i< data_select.length; i++)
    {
        td_right = td_right + '<option value="'+ data_select[i]["id_tag"]+'">'+data_select[i]["tag_name"]+'</option>'
    }
    td_right = td_right + '</select></td>'
    return td_right
};

function addTab(tab,table){
    for(var i = 0; i<tab.length;i++){
        table.append(tab[i]);
    }
};

var add = function(app) {
    var tab = []
    i=0
    $('#user input[type="checkbox"]:checked').each(function(){
        if (app != null){
            var Row = $(this).parents('tr').append(fill_select())
        }else{
            var Row = $(this).parents('tr').append()
        }
        tab.push(Row[0]);
        $("#user").find("input[type=checkbox]:checked").prop('checked', false);
        var ID=$(this).parents('tr').find('td:eq(1)').html();
        tab_add.push(ID);
        
        if (isInTabb(tab_del,ID) == true){
            tab_del.splice(tab_del.indexOf(ID),1);
            tab_add.splice(tab_add.indexOf(ID),1);
        }
    });
    var table = $('#adding_table')
    addTab(tab,table)
};

var del = function(app){
    var tab = []
    $('#adding_table input[type="checkbox"]:checked').each(function(){
        var Row = $(this).parents('tr');
        var ID=$(this).parents('tr').find('td:eq(1)').html();
        var RIGHT = $(this).parents('tr').find("option:selected").val()
        if (app != null){
            right.push({id_user : ID, id_right:RIGHT })
            Row.find('.right').remove()

        }
        var Row = $(this).parents('tr');
        tab.push(Row[0]);
        $("#adding_table").find("input[type=checkbox]:checked").prop('checked', false);
        tab_del.push(ID)
        if (isInTabb(tab_add,ID) == true){
            tab_add.splice(tab_add.indexOf(ID),1);
            tab_del.splice(tab_del.indexOf(ID),1);
        }
    });
    var table = $('#user')
    addTab(tab,table)
};

var update = function(){
    var data ={};
    data["tab_add"] = tab_add;
    data["tab_del"]= tab_del;

    $.ajax({
        url : $(location).attr('href'),
        type : 'post',
        data : JSON.stringify(data),
        contentType:"application/json; charset=utf-8",
        dataType:"json",
        success: function (msg) {
            toastr.options = { 
                "positionClass": "toast-top-center", 
                onHidden : function () {  
                    window.location.href = $(location).attr('href'); 
                } 
            };
            toastr.success(msg.msg + "<br />La page va se recharger", 'Ok !');
            
            
        },
        error: function (msg) {
            toastr.options = {
                "positionClass": "toast-top-center",
                onHidden: function () {
                    window.location.href = $(location).attr('href');
                }
            };
            toastr.error(msg.msg + + "<br />La page va se recharger", 'Shiiiit !');
        }
    })

    tab_add = [];
    tab_del = [];
};

function isInTabb(tab,id){
    var bool = false
    tab.forEach(element => {
        if (element == id){
            bool = true
        }
    });
    return bool
}

var deleteRaw = function (path){
    var c = confirm("Etes vous sur de vouloir supprimer cet élement ? ");
    if (c == true)
       window.location.href = path;
}

$( document ).ready(function() {

    var tab_add = []
    var tab_del = []
    var data_select = {}

    $('#user').DataTable({
        "language": {
            "lengthMenu": "Afficher _MENU_ éléments par page",
            "zeroRecords": "Aucunes données",
            "info": "Page _PAGE_ sur _PAGES_",
            "infoEmpty": "Aucunes données trouvées",
            "infoFiltered": "(filtrer sur _MAX_ total d'éléments)",
            "search":         "Recherche:",
            "paginate": {
                "first":      "Première",
                "last":       "Dernière",
                "next":       "Suivante",
                "previous":   "Précédente"
            },
            "aLengthMenu": [[10, 25, 50, 75, -1], [10, 25, 50, 75, "All"]],
            "iDisplayLength": 25
        }
    });

    $('#adding_table').DataTable({
        "language": {
            "lengthMenu": "Afficher _MENU_ éléments par page",
            "zeroRecords": "Aucunes données",
            "info": "Page _PAGE_ sur _PAGES_",
            "infoEmpty": "Aucunes données",
            "infoFiltered": "(filtrer sur _MAX_ total d'éléments)",
            "search":         "Recherche:",
            "paginate": {
                "first":      "Première",
                "last":       "Dernière",
                "next":       "Suivante",
                "previous":   "Précédente"
            },
            "aLengthMenu": [[10,25, 50, 75, -1], [10,25, 50, 75, "All"]],
            "iDisplayLength": 25
        }
    } );

    $('#tri').DataTable({
        "scrollY": "400px",
        "scrollCollapse": true,
        "paging": true,
        "language": {
            "lengthMenu": "Afficher _MENU_ éléments par page",
            "zeroRecords": "Aucunes données",
            "info": "Page _PAGE_ sur _PAGES_",
            "infoEmpty": "Aucunes données",
            "infoFiltered": "(filtrer sur _MAX_ total d'éléments)",
            "search":         "Recherche:",
            "paginate": {
                "first":      "Première",
                "last":       "Dernière",
                "next":       "Suivante",
                "previous":   "Précédente"
            },
            "aLengthMenu": [[10,25, 50, 75, -1], [10,25, 50, 75, "All"]],
            "iDisplayLength": 25
        }
    });
});

