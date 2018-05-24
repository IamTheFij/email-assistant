<template>
    <v-data-table
        :headers="headers"
        :items="tableItems">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.date }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.type }}</td>
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
                    text: '#',
                    value: 'id',
                },
                {
                    text: 'Date',
                    value: 'date',
                },
                {
                    text: 'Name',
                    value: 'name',
                },
                {
                    text: 'Type',
                    value: 'type',
                },
                {
                    text: '',
                    value: '',
                },
            ],
        };
    },
    methods: {
        formatDigitalDocument(item) {
            return {
                id: item.metadata.identifier,
                date: moment(item.metadata.dateCreated).local().format('HH:mm DD/MM/YYYY'),
                name: item.metadata.name,
                type: item.metadata.additionalType,
                url: item.metadata.url,
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>
