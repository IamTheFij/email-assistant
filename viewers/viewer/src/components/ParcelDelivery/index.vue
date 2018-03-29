<template>
    <v-data-table
        :headers="headers"
        :items="tableItems">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.id }}</td>
            <td>
                <a v-if="props.item.trackingUrl" :href="props.item.trackingUrl">
                    {{ props.item.token }}
                </a>
                <template v-else>
                    {{ props.item.token }}
                </template>
            </td>
            <td>{{ props.item.carrier }}</td>
            <td>{{ props.item.status }}</td>
            <td>{{ props.item.location }}</td>
            <td>{{ props.item.subject }}</td>
        </template>
    </v-data-table>
</template>

<script>
export default {
    computed: {
        tableItems() {
            return this.items.map(this.formatParcelDeliveryItem);
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
                    text: 'Tracking number',
                    value: 'trackingNumber',
                },
                {
                    text: 'Carrier',
                    value: 'carrier',
                },
                {
                    text: 'Status',
                    value: 'status',
                },
                {
                    text: 'Location',
                    value: 'location',
                },
                {
                    text: 'Subject',
                    value: 'subject',
                },
            ],
        };
    },
    methods: {
        formatParcelDeliveryItem(item) {
            return {
                id: item.id,
                trackingUrl: item.metadata.trackingUrl,
                token: item.token,
                carrier: item.metadata.provider.name,
                status: '?',
                location: '?',
                subject: item.subject,
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>
