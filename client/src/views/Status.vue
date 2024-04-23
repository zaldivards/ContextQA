<template>
    <div class="my-2 justify-content-center">
        <div class="px-3 lg:px-0 w-screen lg:w-10 m-auto">
            <h1>Status of ContextQA components</h1>
            <div class="grid w-full">
                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 1
                        <span class="absolute border-circle bg-green-500 lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-1" />
                    </div>
                </div>
                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 2
                        <span class="absolute border-circle bg-green-500 lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-1" />
                    </div>
                </div>
                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 3
                        <span class="absolute border-circle bg-green-500 lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-1" />
                    </div>
                </div>

                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 4
                        <span class="absolute border-circle bg-green-500 lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-1" />
                    </div>
                </div>
                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 5
                        <span class="absolute border-circle bg-green-500 lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-1" />
                    </div>
                </div>
                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 6
                        <span class="absolute border-circle bg-green-500 lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-1" />
                    </div>
                </div>

                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 7
                        <span class="absolute border-circle bg-green-500 lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-1" />
                    </div>
                </div>
                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 8
                        <span class="absolute border-circle bg-green-500 lg:w-2rem w-1rem lg:h-2rem h-1rem positioned border-1" />
                    </div>
                </div>
                <div class="lg:col-4 lg:p-4 md:p-2 md:col-6 col-6">
                    <div class="relative shadow-5 h-10rem border-round-xl align-content-center text-center bg-black-alpha-40">
                        Status 9
                        <span class="absolute border-circle bg-red-500 w-2rem h-2rem positioned border-1" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'StatusView',
}
</script>

<style scoped>
.positioned {
    bottom: -5px;
    right: -5px;
}
</style>