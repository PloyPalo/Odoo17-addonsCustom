/* @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { useState , onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { isNull } from "@web/views/utils";
import { ProjectProjectKanbanRenderer } from "@project/views/project_project_kanban/project_project_kanban_renderer";

patch(ProjectProjectKanbanRenderer.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            ...this.state,
            stage_ids: []
        })
        onWillStart(async () => {
            this.state.stage_ids = await this.orm.call('project.project.stage', 'get_stage_ids', [
                []
            ]);
            // Make sure the first option is selected by default.
        });
    },
    /**
     * Called when the phone number is clicked.
     *
     * @private
     * @param {MouseEvent} ev
     */
    getGroupsOrRecords() {
        const {
            list
        } = this.props;
        if (list.isGrouped) {
            const groups = [...list.groups]
                .sort((a, b) => (a.value && !b.value ? 1 : !a.value && b.value ? -1 : 0))
                .map((group, i) => ({
                    group,
                    key: isNull(group.value) ? `group_key_${i}` : String(group.value),
                }))
            return list.resModel === 'project.project' ?
                groups.filter(item => this.state.stage_ids.includes(Number(item.key))) :
                groups;
        } else {
            return list.records.map((record) => ({ record, key: record.id }));
        }
    }

});