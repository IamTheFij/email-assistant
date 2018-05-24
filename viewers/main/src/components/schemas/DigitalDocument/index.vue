<template>
    <v-data-table
        :headers="headers"
        :items="tableItems"
        :pagination.sync="pagination">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.date }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.id }}</td>
            <td>
                <v-btn :download="props.item.filename" :href="props.item.url" icon v-if="props.item.url">
                    <v-icon>file_download</v-icon>
                </v-btn>
            </td>
        </template>
    </v-data-table>
</template>

<script>
import moment from 'moment';

export default {
    computed: {
        tableItems() {
            return this.items.map(this.formatDigitalDocument);
        },
    },
    data() {
        return {
            headers: [
                {
                    text: 'Date',
                    value: 'date',
                },
                {
                    text: 'Name',
                    value: 'name',
                },
                {
                    text: '#',
                    value: 'id',
                },
                {
                    text: '',
                    value: '',
                    sortable: false,
                },
            ],
            pagination: {
                sortBy: 'date',
                descending: true,
            },
        };
    },
    methods: {
        formatDigitalDocument(item) {
            return {
                id: item.metadata.identifier,
                date: item.metadata.dateCreated,
                name: item.metadata.name,
                url: item.metadata.url,
            };
        },
        formatDate(date) {
            return moment(date).local().format('DD/MM/YYYY');
        },
    },
    props: {
        items: Array,
    },
};
</script>
