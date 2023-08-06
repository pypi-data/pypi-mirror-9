/* Показ списка разрешений для пользовательской роли */
function contextMenu_ShowPermissions(){
	var grid = Ext.getCmp('{{ component.grid.client_id }}');
	Ext.Ajax.request({
       url: '{{ component.grid.action_show_permissions.absolute_url }}',
       params: Ext.applyIf({ {{component.grid.row_id_name}}: grid.getSelectionModel().getSelected().id},{% if component.action_context %}{{component.action_context.json|safe}}{% else %}{}{% endif %}),
       success: function(response, opts){ smart_eval(response.responseText); },
       failure: function(){Ext.Msg.show({title:'', msg: 'Не удалось показать список разрешений.<br>Причина: сервер временно недоступен.', buttons:Ext.Msg.OK, icon: Ext.Msg.WARNING});}
    });
}

function contextMenu_ShowAssignedUsers(){
	var grid = Ext.getCmp('{{ component.grid.client_id }}');
    if(!grid.getSelectionModel().getSelected()){Ext.Msg.show({title: 'Показ пользователей',msg: 'Необходимо выбрать роль.',buttons: Ext.Msg.OK,icon: Ext.MessageBox.INFO});return;};
    if(grid.getSelectionModel().getSelections().length>1){Ext.Msg.show({title: 'Показ пользователей',msg: 'Необходимо выбрать только одну роль.',buttons: Ext.Msg.OK,icon: Ext.MessageBox.INFO});return;}
    Ext.Ajax.request({
       url: '{{ component.grid.action_show_assigned_users.absolute_url }}',
       params: Ext.applyIf({ {{component.grid.row_id_name}}: grid.getSelectionModel().getSelected().id},{% if component.action_context %}{{component.action_context.json|safe}}{% else %}{}{% endif %}),
       success: function(response, opts){ smart_eval(response.responseText); },
       failure: function(){Ext.Msg.show({title:'', msg: 'Не удалось показать список пользователей.<br>Причина: сервер временно недоступен.', buttons:Ext.Msg.OK, icon: Ext.Msg.WARNING});}
    });
}