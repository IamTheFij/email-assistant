<template>
    <v-data-table
        :headers="headers"
        :items="tableItems">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.organizationName }}</td>
            <td>{{ props.item.programName }}</td>
            <td>{{ props.item.memberName }}</td>
            <td>{{ props.item.membershipNumber }}</td>
            <td><img :src="props.item.image" v-if="props.item.image"/></td>
        </template>
    </v-data-table>
</template>

<script>
export default {
    computed: {
        tableItems() {
            return this.items.map(this.formatItem);
        },
    },
    data() {
        return {
            headers: [
                {
                    text: '#',
                    value: 'id',
                },
                {
                    text: 'Organization name',
                    value: 'organizationName',
                },
                {
                    text: 'Program name',
                    value: 'programName',
                },
                {
                    text: 'Member name',
                    value: 'memberName',
                },
                {
                    text: 'Membership number',
                    value: 'membershipNumber',
                },
                {
                    text: 'Image',
                    value: 'image',
                },
            ],
        };
    },
    methods: {
        formatItem(item) {
            return {
                id: item.id,
                organizationName: item.metadata.hostingOrganization.name,
                programName: item.metadata.programName,
                memberName: item.metadata.member.name,
                membershipNumber: item.metadata.membershipNumber,
                image: item.metadata.image,
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>

<style scoped>
img {
    max-height: 100px;
    max-width: 100px;
}
</style>
