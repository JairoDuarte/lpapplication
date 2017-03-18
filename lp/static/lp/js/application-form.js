window._initApplicationForm = window._initApplictaionForm || function(
    diplomeChoisi, filiereDiplomeChoisie, optionDiplomeChoisie,
    filiereChoisie, arbreDiplome, filieres
) {
    var typeDiplomeSelect = $('#id_type_diplome'),
        filiereDiplomeSelect = $('#id_filiere_diplome'),
        optionDiplomeSelect = $('#id_option_diplome'),
        filieresSelect = $('#id_filiere_choisie'),
        typeBacSelect = $('#id_type_bac');

    // On remplie la liste des types de diplomes
    typeDiplomeSelect.empty();
    for (var typeVal in arbreDiplome) {
        var typeDiplome = arbreDiplome[typeVal];
        $('<option/>')
            .attr('value', typeVal)
            .text(typeDiplome.label)
            .prop('selected', diplomeChoisi == typeVal)
            .appendTo(typeDiplomeSelect);
    }
    var otherSelect = $('<option/>')
        .attr('value', '-1')
        .text('Autre...')
        .prop('selected', diplomeChoisi == '-1')
        .appendTo(typeDiplomeSelect);

    // On remplie la liste des filières
    function updateFilieresDiplome() {
        var newVal = typeDiplomeSelect.val();

        if (newVal == '-1') {
            // Si l'on sélectionne le choix `Autres...`
            $('.field-type_diplome_autre').removeClass('hidden');
            filiereDiplomeSelect.empty().prop('disabled', true);
            optionDiplomeSelect.empty().prop('disabled', true);
        }
        else {
            $('.field-type_diplome_autre').addClass('hidden');
            var type = arbreDiplome[newVal];
            if (type) {
                var specialties = type.filieres;
                filiereDiplomeSelect.empty();

                var empty = true;
                for (var specialtyVal in specialties) {
                    var specialty = specialties[specialtyVal];
                    $('<option/>')
                            .attr('value', specialtyVal)
                            .text(specialty.label)
                            .prop('selected', filiereDiplomeChoisie == specialtyVal)
                            .appendTo(filiereDiplomeSelect);
                    empty = false;
                }

                filiereDiplomeSelect.prop('disabled', empty);
            }
            else {
                filiereDiplomeSelect.empty().prop('disabled', true);
            }
        }

        filiereDiplomeChoisie = undefined;
        updateOptionsDiplome();
    }

    // On remplie la liste des options
    function updateOptionsDiplome() {
        var typeVal = typeDiplomeSelect.val();
        var newVal = filiereDiplomeSelect.val();

        if (newVal == '-1') {
            // Si l'on sélectionne le choix `Autres...`
            $('.field-filiere_diplome_autre').removeClass('hidden');
            optionDiplomeSelect.empty().prop('disabled', true);
        }
        else {
            $('.field-filiere_diplome_autre').addClass('hidden');
            var specialty = arbreDiplome[typeVal] && arbreDiplome[typeVal].filieres[newVal];
            if (specialty) {
                var options = specialty.options;
                optionDiplomeSelect.empty();

                var empty = true;
                for (var optionVal in options) {
                    var option = options[optionVal];
                    $('<option/>')
                        .attr('value', optionVal)
                        .text(option)
                        .prop('selected', optionDiplomeChoisie == optionVal)
                        .appendTo(optionDiplomeSelect);
                    empty = false;
                }

                optionDiplomeSelect.prop('disabled', empty);
            }
            else {
                optionDiplomeSelect.empty().prop('disabled', true);
            }
        }

        optionDiplomeChoisie = undefined;
        updateFilieres();
    }

    // On remplie la liste des filières disponibles
    function updateFilieres() {
        var typeDiplome = typeDiplomeSelect.val(),
            filiereDiplome = filiereDiplomeSelect.val(),
            optionDiplome = optionDiplomeSelect.val();

        // On vide le champs de tous les choix
        filieresSelect.empty().prop('disabled', false);

        // On essaye de trouver les filières corréspondantes au diplome choisi
        for (var id in filieres) {
            var filiere = filieres[id];
            if (
                filiere.diplomes.indexOf(typeDiplome) >= 0 ||
                filiere.filieres.indexOf(filiereDiplome) >= 0 ||
                filiere.options.indexOf(filiereDiplome) >= 0
            ) {
                $('<option/>')
                    .attr('value', id)
                    .text(filiere.label)
                    // .prop('selected', selectedFiliere == id)
                    .appendTo(filieresSelect);
            }
        }

        if (filieresSelect.is(':empty')) {
            // TODO: Afficher un erreur une erreur comme quoi il n'ya pas
            // de filière correspondante.
            // TODO: Façon pour administrateurs pour détecter ces cas
            filieresSelect.prop('disabled', true);
        }
    }

    typeDiplomeSelect.on('change', updateFilieresDiplome);
    filiereDiplomeSelect.on('change', updateOptionsDiplome);
    optionDiplomeSelect.on('change', updateFilieres);
    updateFilieresDiplome();

    function updateBacAutreField() {
        var otherField = $('.field-type_bac_autre');
        if (typeBacSelect.val() == '-1') {
            otherField.removeClass('hidden');
        }
        else {
            otherField.addClass('hidden');
        }
    }
    typeBacSelect.on('change', updateBacAutreField);
    updateBacAutreField();
};