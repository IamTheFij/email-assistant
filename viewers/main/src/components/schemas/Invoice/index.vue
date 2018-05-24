<template>
    <v-data-table
        :headers="headers"
        :items="tableItems"
        :pagination.sync="pagination">
        <template slot="items" slot-scope="props">
            <td>{{ formatDate(props.item.date) }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.customer }}</td>
            <td>{{ props.item.payment }}</td>
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
                    text: 'Payment',
                    value: 'payment',
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
                rowsPerPage: 15,
                sortBy: 'date',
                descending: true,
            },
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
                date: item.metadata.date,
                name: item.metadata.name,
                customer: item.metadata.customer ? item.metadata.customer.name : null,
                payment: (
                    item.metadata.totalPaymentDue ?
                    this.formatCurrency(item.metadata.totalPaymentDue) :
                    null
                ),
                url: item.metadata.url,
                filename,
            };
        },
        formatCurrency(cost) {
            if (cost.value) {
                let formattedCost = cost.value;
                if (cost.currency) {
                    formattedCost = `${formattedCost} ${cost.currency}`;
                }
                return formattedCost;
            }
            return null;
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
