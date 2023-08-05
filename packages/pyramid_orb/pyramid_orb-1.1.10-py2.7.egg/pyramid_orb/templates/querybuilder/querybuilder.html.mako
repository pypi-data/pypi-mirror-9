<%page args="id='advanced-btn',title='Advanced'"/>

<button id="${id}"type="button" class="btn btn-default" data-container="body" data-toggle="popover" data-placement="bottom">
    ${title}
</button>

<!-- START RULE TEMPLATE -->
<div id="rule-template" style="display:none">
    <div class="row top-buffer">
        <div class="col-md-1">
            <button type="button" class="btn btn-small btn-default remove-rule-btn">
                <i class="fa fa-remove"></i>
            </button>
        </div>
        <div class="col-md-8">
            <div class="input-group" role="group">
                <select class="selectpicker">
                    <option value="name">Name</option>
                    <option value="created_at">Created At</option>
                </select>
                <select class="selectpicker">
                    <option value="is">Is</option>
                    <option value="is_not">Is Not</option>
                    <option value="is_in">Is In</option>
                    <option selected value="is_not_in">Is Not In</option>
                </select>
                <input class="form-control" type="text"/>
            </div>
        </div>
        <div class="col-md-3">
            <div role="group">
                <button type="button" class="btn btn-block btn-primary and-or-btn">And</button>
            </div>
        </div>
    </div>
</div>

<!-- START BUTTON CONTENTS -->
<div id="${id}-content" class="container" style="display:none">
    <form class="form" role="form">
        <div class="row">
            <div class="col-md-1">
                <button type="button" class="btn btn-small btn-default remove-rule-btn">
                    <i class="fa fa-remove"></i>
                </button>
            </div>
            <div class="col-md-8">
                <div class="input-group" role="group">
                    <select class="selectpicker">
                        <option value="name">Name</option>
                        <option value="created_at">Created At</option>
                    </select>
                    <select class="selectpicker">
                        <option value="is">Is</option>
                        <option value="is_not">Is Not</option>
                    </select>
                    <input class="form-control" type="text"/>
                </div>
            </div>
            <div class="col-md-3">
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-primary and-btn">And</button>
                    <button type="button" class="btn btn-primary or-btn">Or</button>
                </div>
            </div>
        </div>
    </form>
</div>
<!-- END BUTTON CONTENTS -->

<script type="text/javascript">
    $(document).ready(function () {
        function remove_rule(event) {
            $(event.target).closest('.row').remove();
        }

        function add_rule(event) {
            var title = $(event.target).text();
            var content = $(event.target).closest('.popover-content');
            content.append($('#rule-template').html());
            var new_rule = content.children().last();

            // create connections
            new_rule.find('.and-or-btn').click(add_rule);
            new_rule.find('.remove-rule-btn').click(remove_rule);
            console.log(new_rule);

            // update all the optional buttons to the one clicked
            $('.and-or-btn').text(title);
        }

        $('#${id}').popover({
            html : true,
            style : 'width:1200px',
            content : function () {
                return $('#${id}-content').html();
            }
        });
        $('#${id}').on('shown.bs.popover', function () {
            $('.and-btn').click(add_rule);
            $('.or-btn').click(add_rule);
            $('.remove-rule-btn').click(remove_rule);
        });
    });
</script>