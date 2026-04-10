// Copyright (c) 2026 Christian Prior-Mamulyan. Licensed under the Apache License, Version 2.0. See LICENSE in the project root for license information.
namespace PipelineWithDomainModel.Config
{
    public class CodedConfig
    {
    }

    public class InvoiceItem
    {
        public string InvoiceNumber { get; set; }
        public decimal Amount { get; set; }
    }
}
