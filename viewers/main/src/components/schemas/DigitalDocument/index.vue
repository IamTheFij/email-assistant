<template>
    <v-data-table
        :headers="headers"
        :items="tableItems">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.date }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.type }}</td>
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
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>
