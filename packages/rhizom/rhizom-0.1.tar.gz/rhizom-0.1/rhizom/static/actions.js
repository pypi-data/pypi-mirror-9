/*
 * Rhizom - Relationship grapher
 *
 * Copyright (C) 2015  Aurelien Bompard <aurelien@bompard.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/



$(function() {
    $(".alert-dismissible").delay(3000).fadeOut("slow");

    $(".form-table").each(function() { form_table_setup($(this)); });

    /*
    $(".loadable").each(function() {
        $(this).load($(this).attr("data-load-from"), function() {
            $(this).removeClass("loadable");
        });
    });
    */

    // BrowserID
    $(".signin").click(function(e) {
        e.preventDefault();
        navigator.id.request();
    });
    $(".signout").click(function(e) {
        e.preventDefault();
        navigator.id.logout();
    });

});



/*
 * Forms
 */
function form_table_setup(form) {
    form.find("button[type!='submit']").click(function(e) {
        e.preventDefault();
        var button = $(this),
            line = $(this).parents("tr").first(),
            data = {};
        form.find("input[type='hidden']")
            .not(form.find("table input[type='hidden']"))
            .add(line.find("input"))
            .add(line.find("select"))
            .add(button)
            .each(function() {
                var val;
                if ($(this).attr("type") == "checkbox") {
                    val = $(this).is(":checked");
                } else {
                    val = $(this).val();
                }
                data[$(this).attr("name")] = val;
        });
        if (button.attr("data-confirm")) {
            var response = confirm(button.attr("data-confirm"));
            if (!response) return;
        }
        button.button("loading");
        jQuery.post(form.attr("action"), data, function(result) {
            if (result.status == "OK") {
                if (button.val() == "delete") {
                    line.remove();
                } else if (button.val() == "edit") {
                    window.location = window.location;
                }
            } else {
                button.button("reset");
                if (result.message) alert(result.message);
            }
        }, "json");
    });
}



/*
 * BrowserID
 */

navigator.id.watch({
    loggedInUser: currentUser,
    onlogin: function(assertion) {
        // Un utilisateur est connecté ! Voici ce qu'il faut faire :
        // 1. Envoyer l'assertion à votre backend pour vérification et pour créer la session.
        // 2. Mettre à jour l'interface utilisateur.
        $.ajax({
            type: 'POST',
            url: loginUrl,
            data: {assertion: assertion},
            success: function(res, status, xhr) { window.location = res; },
            error: function(xhr, status, err) {
                navigator.id.logout();
                //alert("Login failure: " + err);
            }
        });
    },
    onlogout: function() {
        // Un utilisateur s'est déconnecté ! Voici ce qu'il faut faire :
        // Détruire la session de l'utilisateur en redirigeant l'utilisateur ou en appelant votre backend.
        // Assurez vous aussi de réinitialiser loggedInUser à null sur la prochain fois où la page sera chargée
        // (Pas false, ni 0 ou undefined. null)
        $.ajax({
            type: 'POST',
            url: logoutUrl,
            success: function(res, status, xhr) { window.location = res; },
            error: function(xhr, status, err) { alert("Logout failure: " + err); }
        });
    }
});

