<template>
    <v-data-table
        :headers="headers"
        :items="tableItems">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.reservationNumber }}</td>
            <td>{{ props.item.busNumber }}</td>
            <td>{{ props.item.from }}</td>
            <td>{{ props.item.to }}</td>
            <td><Barcode :value="props.item.boardingPass"></Barcode></td>
            <td>{{ props.item.price }}</td>
        </template>
    </v-data-table>
</template>

<script>
import currencyFormatter from 'currency-formatter';
import moment from 'moment';

import Barcode from '@/components/Barcode';

export default {
    components: {
        Barcode,
    },
    computed: {
        tableItems() {
            return this.items.map(this.formatBusReservationItem);
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
                    text: 'Name',
                    value: 'name',
                },
                {
                    text: 'Reservation number',
                    value: 'reservationNumber',
                },
                {
                    text: 'Bus number',
                    value: 'busNumber',
                },
                {
                    text: 'From',
                    value: 'from',
                },
                {
                    text: 'To',
                    value: 'to',
                },
                {
                    text: 'Boarding pass',
                    value: 'boardingPass',
                },
                {
                    text: 'Price',
                    value: 'priceRaw',
                },
            ],
        };
    },
    methods: {
        formatBusReservationItem(item) {
            const fromStopName = item.metadata.reservationFor.departureBusStop.name;
            const fromDateTime = moment(
                item.metadata.reservationFor.departureTime,
            ).local().format('HH:mm DD/MM/YYYY');
            const from = `${fromStopName} @ ${fromDateTime}`;

            const toStopName = item.metadata.reservationFor.arrivalBusStop.name;
            const toDateTime = moment(
                item.metadata.reservationFor.arrivalTime,
            ).local().format('HH:mm DD/MM/YYYY');
            const to = `${toStopName} @ ${toDateTime}`;

            const price = currencyFormatter.format(
                item.metadata.reservedTicket.price,
                { code: item.metadata.reservedTicket.priceCurrency },
            );

            return {
                id: item.id,
                name: item.metadata.underName.name,
                reservationNumber: item.metadata.reservationNumber,
                busNumber: `${item.metadata.reservationFor.busCompany.name} ${item.metadata.reservationFor.busName} ${item.metadata.reservationFor.busNumber}`,
                from,
                to,
                boardingPass: item.metadata.reservedTicket.ticketToken,
                price,
                priceRaw: item.metadata.reservedTicket.price,
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>
