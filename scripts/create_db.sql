CREATE TABLE "users"(
    "id" SERIAL NOT NULL,
    "keycloack_id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "phone" TEXT NOT NULL,
    "user_type" TEXT NOT NULL,
    "created_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE
    "users" ADD PRIMARY KEY("id");
CREATE TABLE "user_profiles"(
    "user_id" BIGINT NOT NULL,
    "last_name" TEXT NOT NULL,
    "first_name" TEXT NOT NULL,
    "middle_name" TEXT NOT NULL,
    "birth_date" DATE NOT NULL,
    "gender" TEXT NOT NULL
);
ALTER TABLE
    "user_profiles" ADD PRIMARY KEY("user_id");
CREATE TABLE "user_addresses"(
    "id" SERIAL NOT NULL,
    "user_id" BIGINT NOT NULL,
    "region" TEXT NOT NULL,
    "city" TEXT NOT NULL,
    "street" TEXT NOT NULL,
    "house" TEXT NOT NULL,
    "flat" TEXT NOT NULL,
    "residents_counts" INTEGER NOT NULL,
    "area" FLOAT(53) NOT NULL,
    "created_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE
    "user_addresses" ADD PRIMARY KEY("id");
CREATE TABLE "providers"(
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "inn" TEXT NOT NULL,
    "ogrn" TEXT NOT NULL,
    "created_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE
    "providers" ADD PRIMARY KEY("id");
CREATE TABLE "accounts"(
    "id" SERIAL NOT NULL,
    "user_id" BIGINT NOT NULL,
    "account_number" TEXT NOT NULL,
    "address_id" BIGINT NOT NULL,
    "provider_id" BIGINT NOT NULL,
    "created_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "is_active" BOOLEAN NOT NULL,
    "is_deleted" BOOLEAN NOT NULL
);
ALTER TABLE
    "accounts" ADD PRIMARY KEY("id");
CREATE TABLE "bills"(
    "id" SERIAL NOT NULL,
    "account_id" BIGINT NOT NULL,
    "service_id" BIGINT NOT NULL,
    "period" DATE NOT NULL,
    "amount" DECIMAL(8, 2) NOT NULL,
    "status_type" TEXT NOT NULL,
    "last_data" FLOAT(53) NOT NULL,
    "units" FLOAT(53) NOT NULL
);
ALTER TABLE
    "bills" ADD PRIMARY KEY("id");
CREATE TABLE "payments"(
    "id" SERIAL NOT NULL,
    "account_id" BIGINT NOT NULL,
    "amount" BIGINT NOT NULL,
    "paid_at" TIMESTAMP(0) WITHOUT TIME ZONE,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "created_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);
ALTER TABLE
    "payments" ADD PRIMARY KEY("id");
CREATE TABLE "payment_bills"(
    "id" SERIAL NOT NULL,
    "payment_id" BIGINT NOT NULL,
    "bill_id" BIGINT NOT NULL
);
ALTER TABLE
    "payment_bills" ADD PRIMARY KEY("id");
CREATE TABLE "services"(
    "id" SERIAL NOT NULL,
    "service_name" TEXT NOT NULL,
    "provider_id" BIGINT NOT NULL,
    "cost_per_unit" FLOAT(53) NOT NULL
);
ALTER TABLE
    "services" ADD PRIMARY KEY("id");
ALTER TABLE
    "accounts" ADD CONSTRAINT "accounts_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("id");
ALTER TABLE
    "user_addresses" ADD CONSTRAINT "user_addresses_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("id");
ALTER TABLE
    "bills" ADD CONSTRAINT "bills_account_id_foreign" FOREIGN KEY("account_id") REFERENCES "accounts"("id");
ALTER TABLE
    "bills" ADD CONSTRAINT "bills_service_id_foreign" FOREIGN KEY("service_id") REFERENCES "services"("id");
ALTER TABLE
    "accounts" ADD CONSTRAINT "accounts_address_id_foreign" FOREIGN KEY("address_id") REFERENCES "user_addresses"("id");
ALTER TABLE
    "payment_bills" ADD CONSTRAINT "payment_bills_payment_id_foreign" FOREIGN KEY("payment_id") REFERENCES "payments"("id");
ALTER TABLE
    "payment_bills" ADD CONSTRAINT "payment_bills_bill_id_foreign" FOREIGN KEY("bill_id") REFERENCES "bills"("id");
ALTER TABLE
    "accounts" ADD CONSTRAINT "accounts_provider_id_foreign" FOREIGN KEY("provider_id") REFERENCES "providers"("id");
ALTER TABLE
    "payments" ADD CONSTRAINT "payments_account_id_foreign" FOREIGN KEY("account_id") REFERENCES "accounts"("id");
ALTER TABLE
    "services" ADD CONSTRAINT "services_provider_id_foreign" FOREIGN KEY("provider_id") REFERENCES "providers"("id");
ALTER TABLE
    "users" ADD CONSTRAINT "users_id_foreign" FOREIGN KEY("id") REFERENCES "user_profiles"("user_id");