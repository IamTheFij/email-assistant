<template>
    <v-data-table
        :headers="headers"
        :items="tableItems">
        <template slot="items" slot-scope="props">
            <td>{{ props.item.id }}</td>
            <td>{{ props.item.name }}</td>
            <td>{{ props.item.reservationNumber }}</td>
            <td>{{ props.item.flightNumber }}</td>
            <td>{{ props.item.from }}</td>
            <td>{{ props.item.to }}</td>
            <td>{{ props.item.seat }}</td>
            <td><Barcode :value="props.item.boardingPass"></Barcode></td>
        </template>
    </v-data-table>
</template>

<script>
import moment from 'moment';

import Barcode from '@/components/Barcode';

export default {
    components: {
        Barcode,
    },
    computed: {
        tableItems() {
            return this.items.map(this.formatFlightReservationItem);
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
                    text: 'Flight number',
                    value: 'flightNumber',
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
                    text: 'Seat',
                    value: 'seat',
                },
                {
                    text: 'Boarding pass',
                    value: 'boardingPass',
                },
            ],
        };
    },
    methods: {
        formatFlightReservationItem(item) {
            const fromAirport = item.metadata.reservationFor.departureAirport.iataCode;
            const fromTerminal = item.metadata.reservationFor.departureTerminal;
            const fromGate = item.metadata.reservationFor.departureGate;
            const fromDateTime = moment(
                item.metadata.reservationFor.departureTime,
            ).local().format('HH:mm DD/MM/YYYY');
            const from = `${fromAirport} ${fromTerminal} ${fromGate} @ ${fromDateTime}`;

            const toAirport = item.metadata.reservationFor.arrivalAirport.iataCode;
            const toDateTime = moment(
                item.metadata.reservationFor.arrivalTime,
            ).local().format('HH:mm DD/MM/YYYY');
            const to = `${toAirport} @ ${toDateTime}`;

            return {
                id: item.id,
                name: item.metadata.underName.name,
                reservationNumber: item.metadata.reservationNumber,
                flightNumber: `${item.metadata.reservationFor.airline.iataCode} ${item.metadata.reservationFor.flightNumber}`,
                from,
                to,
                seat: item.metadata.airplaneSeat,
                boardingPass: item.metadata.ticketToken,
            };
        },
    },
    props: {
        items: Array,
    },
};
</script>
