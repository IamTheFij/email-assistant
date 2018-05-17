<template>
    <v-data-table
        :headers="headers"
        :items="tableItems">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.date }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.customer }}</td>
            <td>
                <v-btn :download="props.item.filename" :href="props.item.url" icon v-if="props.item.url">
                    <v-icon>file_download</v-icon>
                </v-btn>
            </td>
        </template>
    </v-data-table>
</template>

<script>
import mime from 'mime-types';
import moment from 'moment';

export default {
    computed: {
        tableItems() {
            return this.items.map(this.formatInvoice);
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
                    text: 'Customer',
                    value: 'customer',
                },
                {
                    text: '',
                    value: '',
                },
            ],
        };
    },
    methods: {
        formatInvoice(item) {
            let filename = null;
            if (item.metadata.url) {
                const extension = mime.extension(item.metadata.url.split(':')[1].split(';')[0]);
                filename = `${item.metadata.identifier}.${extension}`;
            }

            return {
                id: item.metadata.identifier,
                date: moment(item.metadata.date).local().format('HH:mm DD/MM/YYYY'),
                name: item.metadata.name,
                customer: item.metadata.customer.name,
                url: item.metadata.url,
                filename,
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>
