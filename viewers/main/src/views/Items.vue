<template>
    <div v-if="isLoading">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    <div v-else>
        <component :items="items" :is="schemas[$route.params.type].component"></component>
    </div>
</template>

<script>
import * as schemas from '@/components/schemas';

export default {
    components: Object.assign({}, schemas.default),
    created() {
        this.fetchItems();
    },
    watch: {
        $route: 'fetchItems',
    },
    data() {
        return {
            isLoading: false,
            items: [],
            schemas: schemas.default,
        };
    },
    methods: {
        fetchItems() {
            this.isLoading = true;
            const headers = new Headers({});
            if (process.env.INDEXER_TOKEN) {
                headers.set('Authorization', `Bearer ${process.env.INDEXER_TOKEN}`);
            }

            fetch(
                `${process.env.INDEXER_URL}/token?filter_type=${this.$route.params.type}`,
                { headers },
            )
                .then(r => r.json())
                .then((r) => {
                    this.isLoading = false;
                    this.items = r.tokens;
                });
        },
    },
};
</script>
