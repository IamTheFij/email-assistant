<template>
    <a :href="parsedBarcode.url" v-if="parsedBarcode.url">
        <img :src="parsedBarcode.url"></img>
    </a>
    <canvas ref="mycanvas" v-else-if="parsedBarcode.bcid"></canvas>
</template>

<script>
import bwipjs from 'bwip-js';

export default {
    computed: {
        parsedBarcode() {
            if (this.value.startsWith('http://') || this.value.startsWith('https://') || this.value.startsWith('//')) {
                // Check if it is a valid URL
                return {
                    url: this.value,
                };
            }
            // Otherwise parse it as a barcode type and data
            const parsed = this.value.split(':', 2);
            if (parsed.length > 1) {
                return {
                    bcid: parsed[0],
                    text: parsed[1],
                };
            }
            return {};
        },
    },
    methods: {
        showBarcode() {
            if (this.parsedBarcode.url) {
                // Just display an image
            } else if (this.parsedBarcode.bcid) {
                // Compute the barcode from bwip
                bwipjs(this.$refs.mycanvas, {
                    bcid: this.parsedBarcode.bcid.toLowerCase(),
                    text: this.parsedBarcode.text,
                    scale: 1.0 / 2.835,  // 72 DPI
                    height: 100,  // In mm
                    width: 100,
                }, (err) => {
                    if (err) {
                        console.error(err);
                    }
                });
            }
        },
    },
    mounted() {
        this.showBarcode();
    },
    updated() {
        this.showBarcode();
    },
    props: {
        value: String,
    },
};
</script>

<style scoped>
img {
    max-height: 100px;
    max-width: 100px;
}
</style>
